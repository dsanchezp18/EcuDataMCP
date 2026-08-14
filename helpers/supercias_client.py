"""Client for the Superintendencia de Compañías, Valores y Seguros company registry.

Supercías publishes the full "Directorio de Companias" (226k+ companies) as a
single static Excel export, refreshed daily, with no auth or pagination
needed:
https://mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx

That file (~35 MB) can't be parsed with openpyxl's normal `read_only=True`
streaming mode: the worksheet's `<dimension>` tag is wrong (it declares only
"A1" even though the sheet has 226k+ rows), which makes openpyxl's read-only
iterator stop after a single row. A full (non-read-only) load works but takes
roughly a minute for a file this size. Instead, `_parse_xlsx` streams the
worksheet XML directly with `ElementTree.iterparse`, which is correct
regardless of the bad dimension tag and several times faster.

The export also has a few title/metadata rows (report name, row count,
generation timestamp) before the real header row, so the header is detected
by content — a row containing both "RUC" and "NOMBRE" once normalized — not
assumed to be a fixed row number.

Because parsing 226k rows takes several seconds even with the fast path, the
full parsed table is cached in memory (see `_companias_cache`) rather than
re-fetched per call. That cache holds the entire registry as one row list
plus a RUC index, which is a non-trivial amount of memory (roughly a few
hundred MB) — acceptable since it's built lazily on first use, not at server
startup, but worth knowing if this process runs somewhere memory-constrained.
"""

from __future__ import annotations

import io
import logging
import re
import zipfile
from typing import Any
from unicodedata import category, normalize
from xml.etree import ElementTree as ET

import httpx

from helpers.cache import TtlCache
from helpers.logging import MAIN_LOGGER_NAME
from helpers.user_agent import USER_AGENT

logger = logging.getLogger(MAIN_LOGGER_NAME)

_EXCEL_URL = (
    "https://mercadodevalores.supercias.gob.ec/reportes/excel/directorio_companias.xlsx"
)
_DOWNLOAD_TIMEOUT = 90.0
# The real file is ~35 MB; this is a safety ceiling, not the expected size.
_MAX_DOWNLOAD_BYTES = 80 * 1024 * 1024
_HEADER_SCAN_LIMIT = 20
_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"

# Refreshed daily upstream; a few hours balances staleness against the cost
# of re-downloading/re-parsing ~35 MB.
_companias_cache = TtlCache(ttl_seconds=21600.0, max_entries=1)


def _strip(text: str) -> str:
    nfkd = normalize("NFKD", text or "")
    return "".join(c for c in nfkd if category(c) != "Mn").lower()


def _normalize_header(header: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", _strip(header)).strip("_")


def _col_index(ref: str) -> int:
    """Convert a cell reference like 'AC12' to a 0-based column index."""
    letters = "".join(c for c in ref if c.isalpha())
    idx = 0
    for c in letters:
        idx = idx * 26 + (ord(c.upper()) - ord("A") + 1)
    return idx - 1


def _read_shared_strings(z: zipfile.ZipFile) -> list[str]:
    # Present when strings are stored by index (the real Supercías export);
    # absent for writers that use inline strings instead (e.g. some openpyxl
    # configurations, including this project's own test fixtures).
    if "xl/sharedStrings.xml" not in z.namelist():
        return []
    shared: list[str] = []
    with z.open("xl/sharedStrings.xml") as f:
        for _, elem in ET.iterparse(f):
            if elem.tag == _NS + "si":
                texts = elem.findall(f".//{_NS}t")
                shared.append("".join(t.text or "" for t in texts))
                elem.clear()
    return shared


def _row_cells(elem: ET.Element, shared: list[str]) -> dict[int, str]:
    cells: dict[int, str] = {}
    for c in elem.findall(_NS + "c"):
        ref = c.get("r")
        if not ref:
            continue
        cell_type = c.get("t")
        if cell_type == "inlineStr":
            inline = c.find(_NS + "is")
            if inline is None:
                continue
            texts = inline.findall(f".//{_NS}t")
            cells[_col_index(ref)] = "".join(t.text or "" for t in texts)
            continue
        v = c.find(_NS + "v")
        if v is None or v.text is None:
            continue
        val = v.text
        if cell_type == "s":
            val = shared[int(val)]
        cells[_col_index(ref)] = val
    return cells


def _parse_xlsx(raw: bytes) -> tuple[tuple[str, ...], list[tuple[str, ...]]]:
    """Parse the Supercías directory export into (fields, rows)."""
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        shared = _read_shared_strings(z)
        fields: tuple[str, ...] | None = None
        rows: list[tuple[str, ...]] = []
        scanned = 0
        with z.open("xl/worksheets/sheet1.xml") as f:
            for _, elem in ET.iterparse(f, events=("end",)):
                if elem.tag != _NS + "row":
                    continue
                cells = _row_cells(elem, shared)
                elem.clear()
                if fields is None:
                    scanned += 1
                    if scanned > _HEADER_SCAN_LIMIT:
                        raise ValueError(
                            "No se encontró la fila de encabezado (RUC/NOMBRE) "
                            "en el reporte de Supercías"
                        )
                    max_col = max(cells, default=-1)
                    candidate = tuple(
                        _normalize_header(cells.get(i, "")) for i in range(max_col + 1)
                    )
                    if "ruc" in candidate and "nombre" in candidate:
                        fields = candidate
                    continue
                width = len(fields)
                rows.append(tuple(cells.get(i, "") for i in range(width)))
        if fields is None:
            raise ValueError(
                "No se encontró la fila de encabezado (RUC/NOMBRE) en el "
                "reporte de Supercías"
            )
        return fields, rows


async def _download_full(url: str) -> bytes:
    async with (
        httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
            timeout=_DOWNLOAD_TIMEOUT,
        ) as session,
        session.stream("GET", url) as resp,
    ):
        resp.raise_for_status()
        chunks: list[bytes] = []
        total = 0
        async for chunk in resp.aiter_bytes(chunk_size=256 * 1024):
            chunks.append(chunk)
            total += len(chunk)
            if total > _MAX_DOWNLOAD_BYTES:
                raise ValueError(
                    f"El export de Supercías superó el límite de "
                    f"{_MAX_DOWNLOAD_BYTES // (1024 * 1024)} MB; se abortó la descarga"
                )
    return b"".join(chunks)


async def _fetch_companias() -> tuple[
    tuple[str, ...], list[tuple[str, ...]], dict[str, tuple[str, ...]], list[str]
]:
    """Return (fields, rows, ruc_index, normalized_names), from cache or fresh."""
    cached = _companias_cache.get("companias")
    if cached is not None:
        return cached

    logger.info("Descargando y parseando el directorio de Supercías (~35 MB)")
    raw = await _download_full(_EXCEL_URL)
    fields, rows = _parse_xlsx(raw)
    ruc_pos = fields.index("ruc")
    nombre_pos = fields.index("nombre")
    ruc_index = {row[ruc_pos]: row for row in rows if row[ruc_pos]}
    normalized_names = [_strip(row[nombre_pos]) for row in rows]

    bundle = (fields, rows, ruc_index, normalized_names)
    _companias_cache.set("companias", bundle)
    logger.info("Directorio de Supercías cargado: %d compañías", len(rows))
    return bundle


def _row_to_dict(fields: tuple[str, ...], row: tuple[str, ...]) -> dict[str, str]:
    return dict(zip(fields, row, strict=True))


async def search_companias(
    query: str = "",
    provincia: str = "",
    situacion_legal: str = "",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Search the Supercías company directory client-side.

    Args:
        query: Free text matched (accent-insensitive) against company name or RUC.
        provincia: Optional substring filter on province (accent-insensitive).
        situacion_legal: Optional substring filter on legal status.
        limit: Max results returned.
        offset: Pagination offset over the matched set.
    """
    fields, rows, _, normalized_names = await _fetch_companias()
    ruc_pos = fields.index("ruc")
    provincia_pos = fields.index("provincia")
    situacion_pos = fields.index("situacion_legal")

    q = _strip(query)
    prov = _strip(provincia)
    situ = _strip(situacion_legal)

    matched: list[int] = []
    for i, row in enumerate(rows):
        if q and q not in normalized_names[i] and q not in row[ruc_pos]:
            continue
        if prov and prov not in _strip(row[provincia_pos]):
            continue
        if situ and situ not in _strip(row[situacion_pos]):
            continue
        matched.append(i)

    page = matched[offset : offset + limit]
    return {
        "total": len(matched),
        "offset": offset,
        "source": "Superintendencia de Compañías, Valores y Seguros — Directorio de Companias",
        "url_fuente": _EXCEL_URL,
        "companias": [_row_to_dict(fields, rows[i]) for i in page],
    }


async def get_compania_by_ruc(ruc: str) -> dict[str, str] | None:
    """Look up a single company by exact RUC match."""
    fields, _, ruc_index, _ = await _fetch_companias()
    row = ruc_index.get((ruc or "").strip())
    if row is None:
        return None
    return _row_to_dict(fields, row)
