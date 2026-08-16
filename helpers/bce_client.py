"""Client for Banco Central del Ecuador's BCEData statistical API.

BCEData (https://contenido.bce.fin.ec/bcedata/) is a JS grid app built on
top of a WordPress plugin (bcedata-grid). It isn't publicly documented as
an API, but inspecting its own network traffic shows it's backed by a
clean, versioned, public REST namespace under `/wp-json/bcedata/v1/` that
works with a plain unauthenticated GET (verified with curl, no cookies or
session needed) -- discovered by reading the app's own requests rather than
from any published reference.

Three endpoints, used together:

- `GET /tree` -- a flat list of ~98 catalog nodes (category headers with no
  `id_grupo`, and leaf groups that have one), covering four top-level
  sections: Estadisticas Monetarias y Financieras, Finanzas Publicas,
  Sector Externo (comercio exterior) and Sector Real (PIB, inflacion,
  desempleo, confianza del consumidor, etc). Small and effectively static,
  so the whole tree is cached in memory rather than re-fetched per search.
- `GET /bundle/{id_grupo}` -- metadata for one group: which frequencies
  and units it's available in, the date range it covers per frequency, and
  the list of individual series inside it (a group can hold a single
  series or dozens, broken out under section headers -- e.g. consumer
  confidence split by nacional/urbano/rural x situacion
  presente/futura/confianza del consumidor).
- `GET /grid?id_grupo=X&frecuencia=Y&unidad=Z&desde=YYYY-MM&hasta=YYYY-MM`
  -- the actual time series: one column per period, one row per series.
  Verified that desde/hasta outside the real data range are silently
  clamped to it rather than erroring, so `get_indicador` doesn't need to
  duplicate that clamping -- it only needs sensible defaults when the
  caller omits them, taken from the bundle's own reported range.

An invalid `id_grupo` or `unidad` gets a clean JSON error from the API
itself (`{"code": ..., "message": ..., "data": {"status": ...}}`), which
`_get_json` surfaces as the exception message instead of a generic HTTP
error, so callers get something actionable ("Unidad invalida para
frecuencia") without needing bespoke validation for every combination.
"""

from __future__ import annotations

import logging
from typing import Any
from unicodedata import category, normalize

import httpx

from helpers.cache import TtlCache
from helpers.logging import MAIN_LOGGER_NAME
from helpers.user_agent import USER_AGENT

logger = logging.getLogger(MAIN_LOGGER_NAME)

_BASE_URL = "https://contenido.bce.fin.ec/wp-json/bcedata/v1"
_TIMEOUT = 30.0

# The catalog tree is small (~98 nodes) and rarely changes; a day balances
# staleness against not re-fetching it on every search.
_tree_cache = TtlCache(ttl_seconds=86400.0, max_entries=1)
# Bundles (per-group metadata) change even less often than the tree itself.
_bundle_cache = TtlCache(ttl_seconds=86400.0, max_entries=256)


def _strip(text: str) -> str:
    nfkd = normalize("NFKD", text or "")
    return "".join(c for c in nfkd if category(c) != "Mn").lower()


async def _get_json(
    path: str,
    params: dict[str, Any] | None = None,
    session: httpx.AsyncClient | None = None,
) -> Any:
    own = session is None
    if own:
        session = httpx.AsyncClient(
            headers={"User-Agent": USER_AGENT}, timeout=_TIMEOUT
        )
    assert session is not None
    try:
        resp = await session.get(f"{_BASE_URL}/{path.lstrip('/')}", params=params)
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("message")
            except Exception:
                detail = None
            logger.warning(
                "BCEData %s devolvió %d: %s", path, resp.status_code, detail
            )
            raise ValueError(detail or f"BCEData devolvió HTTP {resp.status_code}")
        return resp.json()
    finally:
        if own:
            await session.aclose()


async def _fetch_tree() -> list[dict[str, Any]]:
    cached = _tree_cache.get("tree")
    if cached is not None:
        return cached
    tree = await _get_json("tree")
    if not isinstance(tree, list):
        raise TypeError("BCEData /tree devolvió un formato inesperado")
    _tree_cache.set("tree", tree)
    return tree


def _index_tree(tree: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten the tree to its leaf groups, each tagged with its section/subsection.

    The tree is a flat list ordered depth-first, with `num_nivel` (1/2/3)
    the only signal of hierarchy -- there are no parent pointers. Walking
    it in order and remembering the last-seen nivel-1/nivel-2 labels
    reconstructs the breadcrumb each leaf belongs to.
    """
    section = ""
    subsection = ""
    indexed: list[dict[str, Any]] = []
    for node in tree:
        nivel = node.get("num_nivel")
        desc = node.get("desc_clasificador", "")
        if nivel == 1:
            section = desc
        elif nivel == 2:
            subsection = desc
        if node.get("id_grupo") is not None:
            indexed.append(
                {
                    "id_grupo": node["id_grupo"],
                    "descripcion": desc,
                    "seccion": section,
                    "subseccion": subsection if subsection != desc else "",
                }
            )
    return indexed


async def _fetch_bundle(id_grupo: int) -> dict[str, Any]:
    cached = _bundle_cache.get(id_grupo)
    if cached is not None:
        return cached
    bundle = await _get_json(f"bundle/{id_grupo}")
    if not isinstance(bundle, dict):
        raise TypeError("BCEData /bundle devolvió un formato inesperado")
    _bundle_cache.set(id_grupo, bundle)
    return bundle


async def search_indicadores(
    query: str = "", limit: int = 20, offset: int = 0
) -> dict[str, Any]:
    """
    Search the BCEData catalog of statistical indicator groups.

    Args:
        query: Free text matched (accent-insensitive) against the group's
            description and its section/subsection in the catalog tree.
        limit: Max results returned.
        offset: Pagination offset over the matched set.
    """
    tree = await _fetch_tree()
    indexed = _index_tree(tree)

    q = _strip(query)
    if q:
        matched = [
            item
            for item in indexed
            if q in _strip(item["descripcion"])
            or q in _strip(item["seccion"])
            or q in _strip(item["subseccion"])
        ]
    else:
        matched = indexed

    page = matched[offset : offset + limit]
    return {"total": len(matched), "offset": offset, "indicadores": page}


async def get_indicador(
    id_grupo: int,
    desde: str = "",
    hasta: str = "",
    frecuencia: str = "",
    unidad: str = "",
) -> dict[str, Any]:
    """
    Time series data for one BCEData indicator group.

    Args:
        id_grupo: The group id from search_indicadores.
        desde: Start period as YYYY-MM. Defaults to the group's earliest
            available period for the chosen frequency.
        hasta: End period as YYYY-MM. Defaults to the group's latest
            available period for the chosen frequency.
        frecuencia: One of the group's available frequencies (Semanal,
            Mensual, Trimestral, Anual). Defaults to the first one the
            group offers.
        unidad: One of the group's available units for the chosen
            frequency (varies by group, e.g. "Millones de USD", "Indice",
            "Porcentaje"). Defaults to the first one available.
    """
    bundle = await _fetch_bundle(id_grupo)
    context = bundle.get("context") or {}
    frecuencias: list[str] = bundle.get("frecuencias") or []
    if not frecuencias:
        return {
            "error": "sin_datos",
            "id_grupo": id_grupo,
            "grupo": context.get("nom_grupo"),
        }

    freq = frecuencia if frecuencia in frecuencias else frecuencias[0]
    unidades_disponibles: list[str] = (bundle.get("unidades") or {}).get(freq, [])
    if not unidades_disponibles:
        return {
            "error": "sin_datos",
            "id_grupo": id_grupo,
            "grupo": context.get("nom_grupo"),
            "frecuencia": freq,
        }
    unit = unidad if unidad in unidades_disponibles else unidades_disponibles[0]

    range_for_freq = (bundle.get("range_by_freq") or {}).get(
        freq, bundle.get("range") or {}
    )
    d = desde.strip() or range_for_freq.get("minYm", "")
    h = hasta.strip() or range_for_freq.get("maxYm", "")

    grid = await _get_json(
        "grid",
        params={
            "id_grupo": id_grupo,
            "frecuencia": freq,
            "unidad": unit,
            "desde": d,
            "hasta": h,
        },
    )

    series = [
        {
            "label": row.get("label"),
            "ruta": row.get("ruta", ""),
            "valores": row.get("values", {}),
        }
        for row in grid.get("rows", [])
        if row.get("tipo") == "Series"
    ]

    return {
        "id_grupo": id_grupo,
        "grupo": context.get("nom_grupo"),
        "frecuencia": freq,
        "unidad": unit,
        "desde": d,
        "hasta": h,
        "periodos": grid.get("columns", []),
        "series": series,
    }
