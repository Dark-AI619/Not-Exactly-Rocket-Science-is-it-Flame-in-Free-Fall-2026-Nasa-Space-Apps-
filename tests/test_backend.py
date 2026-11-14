# Co-authored with ChatGPT
"""Phase 3B service, scientific-preservation, and SQL security tests."""
import hashlib
from pathlib import Path

import pytest

from backend import QueryRejected, ResearchError, ResearchStore, RestrictedSQL, validate_database

ARCHIVE = Path(__file__).resolve().parents[1] / "data" / "flame_research.db.gz"


@pytest.fixture
def store():
    with ResearchStore() as service:
        yield service


def test_integrity_and_coverage(store):
    assert validate_database(store) == {
        "experiments": 273, "measurements": 2457, "passages": 329,
        "sources": 23, "status": "VALIDATED_SUBSET",
    }
    assert len(store.domains()) == 6
    assert len(store.topics("combustion")) >= 8
    assert store.coverage("FLEX")["admitted_experiments"] == 273
    assert store.coverage("BASS-II")["admitted_passages"] == 20
    assert store.coverage("SAFFIRE")["admitted_experiments"] == 0
    with pytest.raises(ResearchError):
        store.coverage("NOT_REAL")


def test_source_catalogue_and_provenance(store):
    assert store.source("PSI-69")["rights_status"] == "CC0-1.0"
    assert store.source("PSI-99")["admission_status"] == "CATALOGUE_ONLY"
    assert len(store.source_evidence("PSI-69")) == 1
    assert store.source_evidence("PSI-99") == []
    assert all(s["domain_id"] == "detection" for s in store.sources(domain_id="detection"))
    assert len(store.sources(investigation_id="FLEX", admitted_only=True)) == 2
    first = store.experiments(limit=1)[0]
    provenance = store.provenance(first["id"])
    assert provenance["source_title"] == "20150023456.pdf"
    assert provenance["first_pdf_page"] == 26
    assert provenance["source_sha256"] == "b4f6ca983e2792c33a0b92220a791a818f426bb635b94f7fd33dc8c9c471e79d"
    detail = store.experiment(first["id"])
    assert len(detail["measurements"]) == 9
    assert detail["data_origin"] == "NASA_REPORT_EXTRACTED"
    assert detail["measurements"][7]["original_unit"] == "mm²/s"
    with pytest.raises(ResearchError):
        store.experiment("UNKNOWN")


def test_parameterized_filters_and_missing_data(store):
    flex = store.experiments(investigation_id="FLEX", limit=500)
    assert len(flex) == 273
    assert store.experiments(investigation_id="BASS-II") == []
    methanol = store.experiments(fuel="Methanol", limit=500)
    assert methanol and all(row["fuel"] == "Methanol" for row in methanol)
    oxygen = store.experiments(oxygen_min=0.2, oxygen_max=0.21, limit=500)
    assert oxygen and all(0.2 <= row["oxygen_mole_fraction"] <= 0.21 for row in oxygen)
    assert store.experiments(test_query="%_") == []
    assert store.experiments(test_query="FLEX", limit=1, offset=1)[0]["id"] == flex[1]["id"]
    with pytest.raises(ResearchError):
        store.experiments(oxygen_min=1.1)
    with pytest.raises(ResearchError):
        store.experiments(pressure_min=float("nan"))
    with pytest.raises(ResearchError):
        store.experiments(limit=501)


def test_fts_topic_scope(store):
    rows = store.passages("droplet", investigation_id="FLEX", topic_id="droplet", limit=10)
    assert rows and all(row["investigation_id"] == "FLEX" for row in rows)
    assert all(row["source_title"] == "20150023456.pdf" for row in rows)
    assert store.passages("droplet", investigation_id="SAFFIRE") == []
    assert [r["id"] for r in store.passages("* OR combustion")] == [
        r["id"] for r in store.passages("OR combustion")
    ]  # Operator text is quoted, never executed as FTS syntax.
    with pytest.raises(ResearchError):
        store.passages("")


def test_numerical_summary_preserves_units_and_missingness(store):
    frame = store.measurement_frame("burn_time_s")
    summary = store.describe_measurement("burn_time_s")
    assert len(frame) == 273
    assert summary["unit"] == "s"
    assert summary["count"] == 267
    assert summary["missing"] == 6
    assert summary["minimum"] == pytest.approx(0.3)
    assert summary["maximum"] == pytest.approx(39.2)
    assert frame.loc[frame["numeric_value"].isna(), "classification"].eq("UNAVAILABLE").all()
    rate = store.measurement_frame("burning_rate_mm2_s")
    assert set(rate["original_unit"]) == {"mm²/s"}
    assert store.describe_measurement("burn_time_s", investigation_id="SAFFIRE")["count"] == 0
    with pytest.raises(ResearchError):
        store.measurement_frame("invented_field")


def test_restricted_sql_allows_bounded_research_queries(store):
    sql = RestrictedSQL(store, max_rows=2)
    result = sql.execute("SELECT id,fuel FROM experiment_records ORDER BY id")
    assert result.columns == ("id", "fuel")
    assert len(result.rows) == 2 and result.truncated
    count = sql.execute(
        "SELECT count(*) AS n FROM measurement_records WHERE variable=?",
        ("oxygen_mole_fraction",),
    )
    assert count.rows == ({"n": 273},)
    assert not count.truncated
    assert sql.execute("SELECT count(*) AS n FROM source_records WHERE domain_id=:domain",
                       {"domain": "detection"}).rows[0]["n"] >= 1
    joined = sql.execute(
        """SELECT e.original_test_id,m.numeric_value
           FROM experiment_records e JOIN measurement_records m
             ON m.experiment_id=e.id
           WHERE m.variable='pressure_mmhg' ORDER BY e.id"""
    )
    assert joined.rows[0]["numeric_value"] == pytest.approx(757.7)
    with pytest.raises(QueryRejected, match="Duplicate output names"):
        sql.execute("SELECT id,id FROM experiment_records LIMIT 1")


@pytest.mark.parametrize("attack", [
    "UPDATE experiment_records SET fuel='X'",
    "DELETE FROM measurement_records",
    "DROP TABLE experiment_records",
    "PRAGMA database_list",
    "ATTACH DATABASE ':memory:' AS other",
    "SELECT name FROM sqlite_master",
    "SELECT * FROM sources",
    "SELECT load_extension('x')",
    "SELECT count(*) FROM experiment_records; DELETE FROM experiment_records",
    "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT max(x) FROM n",
])
def test_restricted_sql_blocks_unsafe_operations(store, attack):
    with pytest.raises(QueryRejected):
        RestrictedSQL(store, timeout_seconds=0.2, max_vm_steps=10_000).execute(attack)


def test_sql_cannot_change_authoritative_archive(store):
    before = hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
    with pytest.raises(QueryRejected):
        RestrictedSQL(store).execute("INSERT INTO experiment_records(id) VALUES ('fake')")
    assert hashlib.sha256(ARCHIVE.read_bytes()).hexdigest() == before
    assert len(store.experiments(limit=500)) == 273
