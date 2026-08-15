import os
import sqlite3
import time

import pytest

from helpers import supercias_financials


def _build_db(path) -> None:
    conn = sqlite3.connect(path)
    conn.execute(
        "CREATE TABLE ranking (anio INTEGER, expediente INTEGER, "
        "posicion_general INTEGER, ciiu_n1 TEXT, ciiu_n6 TEXT, "
        "ingresos_ventas REAL, activos REAL, roe REAL)"
    )
    conn.executemany(
        "INSERT INTO ranking VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (2025, 1, 10, "C", "C1010.01", 1000.0, 5000.0, 0.1),
            (2024, 1, 15, "C", "C1010.01", 900.0, 4800.0, 0.09),
            (2025, 2, 3, "G", "G4510.01", 3000.0, 9000.0, 0.2),
        ],
    )
    conn.execute("CREATE TABLE segmentos (id_segmento INTEGER, segmento TEXT)")
    conn.execute("CREATE TABLE ciiu (ciiu TEXT, descripcion TEXT)")
    conn.execute(
        "CREATE TABLE indicadores_sector (anio INTEGER, ciiu_n1 TEXT, "
        "descripcion TEXT, roe REAL)"
    )
    conn.execute(
        "INSERT INTO indicadores_sector VALUES (2025, 'C', 'Manufactura', 0.08)"
    )
    conn.commit()
    conn.close()


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "financials.sqlite3"
    _build_db(path)
    monkeypatch.setattr(supercias_financials, "DB_PATH", path)
    return path


def test_resolve_expediente_distinguishes_ruc_from_expediente():
    assert supercias_financials._resolve_expediente("123") == 123
    assert supercias_financials._resolve_expediente("1790013731001") is None
    assert supercias_financials._resolve_expediente("") is None
    assert supercias_financials._resolve_expediente("abc") is None


def test_check_db_fresh_missing_file(tmp_path):
    missing = tmp_path / "does_not_exist.sqlite3"
    with pytest.raises(supercias_financials.FinancialsDbUnavailable, match="no existe"):
        supercias_financials._check_db_fresh(missing)


def test_check_db_fresh_stale_file(tmp_path):
    path = tmp_path / "old.sqlite3"
    path.write_bytes(b"")
    old_time = time.time() - 8 * 24 * 3600
    os.utime(path, (old_time, old_time))
    with pytest.raises(
        supercias_financials.FinancialsDbUnavailable, match="desactualizada"
    ):
        supercias_financials._check_db_fresh(path)


async def test_get_financials_by_expediente(db_path, monkeypatch):
    async def fake_get_by_expediente(expediente):
        assert expediente == "1"
        return {"expediente": "1", "nombre": "ACME", "ruc": "999"}

    monkeypatch.setattr(
        supercias_financials.supercias_client,
        "get_compania_by_expediente",
        fake_get_by_expediente,
    )

    result = await supercias_financials.get_financials("1")

    assert result["expediente"] == 1
    assert result["nombre"] == "ACME"
    assert [y["anio"] for y in result["years"]] == [2025, 2024]


async def test_get_financials_by_expediente_not_in_directory(db_path, monkeypatch):
    # Financial data must still come back even if the company predates the
    # directory's own coverage -- only nombre/ruc display is best-effort.
    async def fake_get_by_expediente(expediente):
        return None

    monkeypatch.setattr(
        supercias_financials.supercias_client,
        "get_compania_by_expediente",
        fake_get_by_expediente,
    )

    result = await supercias_financials.get_financials("1")

    assert result["expediente"] == 1
    assert result["nombre"] is None
    assert result["ruc"] is None
    assert [y["anio"] for y in result["years"]] == [2025, 2024]


async def test_get_financials_by_ruc(db_path, monkeypatch):
    async def fake_get_by_ruc(ruc):
        assert ruc == "1790013731001"
        return {"expediente": "2", "nombre": "OTRA S.A.", "ruc": ruc}

    monkeypatch.setattr(
        supercias_financials.supercias_client, "get_compania_by_ruc", fake_get_by_ruc
    )

    result = await supercias_financials.get_financials("1790013731001")

    assert result["expediente"] == 2
    assert result["nombre"] == "OTRA S.A."
    assert len(result["years"]) == 1


async def test_get_financials_ruc_not_found(db_path, monkeypatch):
    async def fake_get_by_ruc(ruc):
        return None

    monkeypatch.setattr(
        supercias_financials.supercias_client, "get_compania_by_ruc", fake_get_by_ruc
    )

    result = await supercias_financials.get_financials("0000000000000")

    assert result["error"] == "not_found"
    assert result["years"] == []


async def test_search_ranking_filters_and_sorts(db_path):
    result = await supercias_financials.search_ranking(anio=2025)
    assert result["total"] == 2
    # Sorted ascending by posicion_general by default.
    assert [c["expediente"] for c in result["companias"]] == [2, 1]


async def test_search_ranking_filters_by_ciiu(db_path):
    result = await supercias_financials.search_ranking(anio=2025, ciiu_n1="c")
    assert result["total"] == 1
    assert result["companias"][0]["expediente"] == 1


async def test_search_ranking_rejects_unknown_order_by(db_path):
    # Falls back to posicion_general instead of raising/injecting SQL.
    result = await supercias_financials.search_ranking(
        anio=2025, order_by="DROP TABLE ranking;--"
    )
    assert result["total"] == 2


async def test_get_sector_benchmark(db_path):
    benchmark = await supercias_financials.get_sector_benchmark(2025, "c")
    assert benchmark is not None
    assert benchmark["descripcion"] == "Manufactura"

    missing = await supercias_financials.get_sector_benchmark(2025, "z")
    assert missing is None
