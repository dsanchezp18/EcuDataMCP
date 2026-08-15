"""Query layer over the Supercías financial-ranking dataset (bi_ranking.csv).

Distinct from helpers/supercias_client.py's company directory: this is the
"Ranking" dataset (https://appscvsmovil.supercias.gob.ec/ranking/reporte.html),
derived from real balance-sheet filings — revenue, assets, equity, profit,
and ~38 financial ratios per company per fiscal year. The directory only has
"capital suscrito"; this has actual financial performance.

The source CSV (bi_ranking.csv) is ~356 MB / ~9M rows covering 2008-present,
too large to hold in memory the way supercias_client.py holds the (also
large, but 10x smaller) company directory. Instead this module only ever
*queries* a local SQLite database that `scripts/build_supercias_financials_db.py`
builds ahead of time, pruned to the last 5 fiscal years during that build.
That script is meant to be run by the server operator before deploying, or
on a periodic schedule (the underlying data refreshes far less often than
the daily-updated company directory) — not lazily inside a request the way
supercias_client.py's TtlCache does, because a from-scratch build downloads
the full 356 MB file and takes minutes, not the ~30-40s that's tolerable
for a single MCP tool call.

Company names/RUCs are resolved via helpers.supercias_client's already-cached
directory (joined on `expediente`) rather than duplicating bi_compania.csv,
which carries the same company fields the directory already has.
"""

from __future__ import annotations

import asyncio
import sqlite3
import time
from pathlib import Path
from typing import Any

from helpers import supercias_client

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "supercias_financials.sqlite3"
# The dataset refreshes far less often than the daily company directory;
# treat a build older than this as stale rather than silently serving it.
_MAX_DB_AGE_SECONDS = 7 * 24 * 3600

_RANKING_COLUMNS = (
    "anio", "expediente", "posicion_general", "cia_imvalores",
    "id_estado_financiero", "ingresos_ventas", "activos", "patrimonio",
    "utilidad_an_imp", "impuesto_renta", "n_empleados", "ingresos_totales",
    "utilidad_ejercicio", "utilidad_neta", "cod_segmento", "ciiu_n1",
    "ciiu_n6", "liquidez_corriente", "prueba_acida", "end_activo",
    "end_patrimonial", "end_activo_fijo", "end_corto_plazo",
    "end_largo_plazo", "cobertura_interes", "apalancamiento",
    "apalancamiento_financiero", "end_patrimonial_ct", "end_patrimonial_nct",
    "apalancamiento_c_l_plazo", "rot_cartera", "rot_activo_fijo",
    "rot_ventas", "per_med_cobranza", "per_med_pago", "impac_gasto_a_v",
    "impac_carga_finan", "rent_neta_activo", "margen_bruto",
    "margen_operacional", "rent_neta_ventas", "rent_ope_patrimonio",
    "rent_ope_activo", "roe", "roa", "fortaleza_patrimonial",
    "gastos_financieros", "gastos_admin_ventas", "depreciaciones",
    "amortizaciones", "costos_ventas_prod", "deuda_total",
    "deuda_total_c_plazo", "total_gastos",
)

_ORDERABLE_COLUMNS = frozenset(_RANKING_COLUMNS)


class FinancialsDbUnavailable(Exception):
    """Raised when the SQLite build is missing or older than _MAX_DB_AGE_SECONDS."""


def _check_db_fresh(path: Path | None = None) -> None:
    # Read the module attribute at call time, not as a bound default -- a
    # default evaluated at def-time would freeze the original DB_PATH value,
    # which breaks tests (and anything else) that monkeypatch DB_PATH.
    if path is None:
        path = DB_PATH
    if not path.exists():
        raise FinancialsDbUnavailable(
            "La base de datos financiera de Supercías no existe todavía. "
            "Corre `python scripts/build_supercias_financials_db.py` en el "
            "servidor y vuelve a intentar (tarda varios minutos la primera vez)."
        )
    age = time.time() - path.stat().st_mtime
    if age > _MAX_DB_AGE_SECONDS:
        days = int(age // 86400)
        raise FinancialsDbUnavailable(
            f"La base de datos financiera de Supercías tiene {days} días de "
            "antigüedad y se considera desactualizada. Corre "
            "`python scripts/build_supercias_financials_db.py` para refrescarla."
        )


def _connect(path: Path | None = None) -> sqlite3.Connection:
    if path is None:
        path = DB_PATH
    _check_db_fresh(path)
    conn = sqlite3.connect(f"file:{path.as_posix()}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _resolve_expediente(value: str) -> int | None:
    """expediente is a small integer; a 13-digit numeric string is a RUC instead."""
    value = (value or "").strip()
    if not value:
        return None
    if value.isdigit() and len(value) != 13:
        return int(value)
    return None


def _row_to_dict(row: sqlite3.Row) -> dict[str, Any]:
    return dict(row)


def _query_financials_by_expediente(
    expediente: int, anio: int | None
) -> list[dict[str, Any]]:
    conn = _connect()
    try:
        if anio is not None:
            cur = conn.execute(
                "SELECT * FROM ranking WHERE expediente = ? AND anio = ? "
                "ORDER BY anio DESC",
                (expediente, anio),
            )
        else:
            cur = conn.execute(
                "SELECT * FROM ranking WHERE expediente = ? ORDER BY anio DESC",
                (expediente,),
            )
        return [_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _query_search_ranking(
    anio: int | None,
    ciiu_n1: str,
    order_by: str,
    limit: int,
    offset: int,
) -> tuple[int, list[dict[str, Any]]]:
    conn = _connect()
    try:
        clauses: list[str] = []
        params: list[Any] = []
        if anio is not None:
            clauses.append("anio = ?")
            params.append(anio)
        if ciiu_n1:
            clauses.append("ciiu_n1 = ?")
            params.append(ciiu_n1.strip().upper())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""

        total = conn.execute(
            f"SELECT COUNT(*) FROM ranking {where}", params
        ).fetchone()[0]

        sort_col = order_by if order_by in _ORDERABLE_COLUMNS else "posicion_general"
        cur = conn.execute(
            f"SELECT * FROM ranking {where} ORDER BY {sort_col} ASC LIMIT ? OFFSET ?",
            (*params, limit, offset),
        )
        return total, [_row_to_dict(r) for r in cur.fetchall()]
    finally:
        conn.close()


def _query_sector_benchmark(anio: int, ciiu_n1: str) -> dict[str, Any] | None:
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT * FROM indicadores_sector WHERE anio = ? AND ciiu_n1 = ?",
            (anio, ciiu_n1.strip().upper()),
        )
        row = cur.fetchone()
        return _row_to_dict(row) if row else None
    finally:
        conn.close()


async def get_financials(
    expediente_or_ruc: str, anio: int | None = None
) -> dict[str, Any]:
    """
    Financial history for a company, most recent fiscal year first.

    Args:
        expediente_or_ruc: Either the company's Supercías "expediente" number
            or its 13-digit RUC (resolved to expediente via the company
            directory).
        anio: Optional single fiscal year filter.
    """
    expediente = _resolve_expediente(expediente_or_ruc)
    compania: dict[str, str] | None = None
    if expediente is None:
        compania = await supercias_client.get_compania_by_ruc(expediente_or_ruc)
        if compania is None:
            return {
                "error": "not_found",
                "expediente_or_ruc": expediente_or_ruc,
                "years": [],
            }
        expediente = int(compania["expediente"])
    else:
        # Best-effort name lookup for display; not fatal if it fails since
        # the expediente given may predate the directory's own coverage.
        compania = await supercias_client.get_compania_by_expediente(str(expediente))

    years = await asyncio.to_thread(
        _query_financials_by_expediente, expediente, anio
    )
    return {
        "expediente": expediente,
        "nombre": compania.get("nombre") if compania else None,
        "ruc": compania.get("ruc") if compania else None,
        "years": years,
    }


async def search_ranking(
    anio: int | None = None,
    ciiu_n1: str = "",
    order_by: str = "posicion_general",
    limit: int = 20,
    offset: int = 0,
) -> dict[str, Any]:
    """
    Filter/rank companies within the cached fiscal years.

    Args:
        anio: Optional fiscal year filter.
        ciiu_n1: Optional CIIU level-1 economic activity filter (single letter).
        order_by: Column to sort by (any ranking column; defaults to the
            dataset's own precomputed posicion_general).
        limit: Max results.
        offset: Pagination offset.
    """
    total, rows = await asyncio.to_thread(
        _query_search_ranking, anio, ciiu_n1, order_by, limit, offset
    )
    return {"total": total, "offset": offset, "companias": rows}


async def get_sector_benchmark(anio: int, ciiu_n1: str) -> dict[str, Any] | None:
    """Sector-level average of the same ratios, for one fiscal year + CIIU level-1."""
    return await asyncio.to_thread(_query_sector_benchmark, anio, ciiu_n1)
