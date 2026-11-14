# Co-authored with ChatGPT
"""Typed, bounded access to the admitted NASA research corpus."""
from __future__ import annotations

import gzip
import math
import re
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd

DEFAULT_ARCHIVE = Path(__file__).resolve().parents[1] / "data" / "flame_research.db.gz"
VARIABLE_UNITS = {
    "pressure_mmhg": "mmHg",
    "oxygen_mole_fraction": "mole fraction",
    "nitrogen_mole_fraction": "mole fraction",
    "carbon_dioxide_mole_fraction": "mole fraction",
    "helium_mole_fraction": "mole fraction",
    "initial_diameter_mm": "mm",
    "visible_extinction_diameter_mm": "mm",
    "burning_rate_mm2_s": "mm²/s",
    "burn_time_s": "s",
}


class ResearchError(ValueError):
    """Invalid filter, unknown record, or failed scientific-integrity check."""


def _bound(limit: int, maximum: int = 500) -> int:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= maximum:
        raise ResearchError(f"limit must be an integer from 1 to {maximum}")
    return limit


def _nonnegative(value: int, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ResearchError(f"{label} must be a nonnegative integer")
    return value


def _finite(value: float | None, label: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ResearchError(f"{label} must be numeric")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ResearchError(f"{label} must be numeric") from exc
    if not math.isfinite(number):
        raise ResearchError(f"{label} must be finite")
    return number


def _rows(cursor: sqlite3.Cursor) -> list[dict]:
    return [dict(row) for row in cursor.fetchall()]


class ResearchStore:
    """Load a read-only SQLite snapshot; never modify the authoritative archive."""

    def __init__(self, path: str | Path = DEFAULT_ARCHIVE):
        self.path = Path(path)
        if not self.path.is_file():
            raise FileNotFoundError(self.path)
        if self.path.suffix == ".gz":
            self.db = sqlite3.connect(":memory:")
            with gzip.open(self.path, "rb") as stream:
                self.db.deserialize(stream.read())
        else:
            uri = self.path.resolve().as_uri() + "?mode=ro"
            self.db = sqlite3.connect(uri, uri=True)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA query_only=ON")

    def close(self) -> None:
        self.db.close()

    def __enter__(self) -> ResearchStore:
        return self

    def __exit__(self, *_exc) -> None:
        self.close()

    def domains(self) -> list[dict]:
        return _rows(self.db.execute("SELECT id,label FROM research_domains ORDER BY label"))

    def topics(self, domain_id: str | None = None) -> list[dict]:
        sql = "SELECT id,domain_id,label FROM research_topics"
        params: list = []
        if domain_id is not None:
            sql += " WHERE domain_id=?"
            params.append(domain_id)
        return _rows(self.db.execute(sql + " ORDER BY label", params))

    def investigations(self, domain_id: str | None = None) -> list[dict]:
        sql = """
            SELECT i.id,i.name,i.doi,i.psi_url,
                   c.admitted_experiments,c.admitted_passages,c.coverage_note
            FROM investigations i JOIN investigation_coverage c ON c.investigation_id=i.id
        """
        params: list = []
        if domain_id is not None:
            sql += " WHERE EXISTS (SELECT 1 FROM source_catalogue s WHERE s.investigation_id=i.id AND s.domain_id=?)"
            params.append(domain_id)
        return _rows(self.db.execute(sql + " ORDER BY i.id", params))

    def coverage(self, investigation_id: str) -> dict:
        row = self.db.execute(
            "SELECT * FROM investigation_coverage WHERE investigation_id=?", (investigation_id,)
        ).fetchone()
        if row is None:
            raise ResearchError(f"unknown investigation: {investigation_id}")
        return dict(row)

    def sources(
        self, *, investigation_id: str | None = None, domain_id: str | None = None,
        topic_id: str | None = None, admitted_only: bool = False, limit: int = 100,
    ) -> list[dict]:
        sql = "SELECT c.* FROM source_catalogue c WHERE 1=1"
        params: list = []
        for column, value in (
            ("investigation_id", investigation_id),
            ("domain_id", domain_id),
        ):
            if value is not None:
                sql += f" AND c.{column}=?"
                params.append(value)
        if topic_id is not None:
            # A source can cover a topic in a page or measurement even when its
            # catalogue's primary topic is broader.
            sql += """ AND (
                c.primary_topic_id=?
                OR EXISTS (
                    SELECT 1 FROM passages p JOIN passage_topics t ON t.passage_id=p.id
                    WHERE p.source_id=c.source_id AND t.topic_id=?
                )
                OR EXISTS (
                    SELECT 1 FROM measurements m JOIN measurement_topics t ON t.measurement_id=m.id
                    WHERE m.source_id=c.source_id AND t.topic_id=?
                )
            )"""
            params.extend((topic_id, topic_id, topic_id))
        if admitted_only:
            sql += " AND admission_status<>'CATALOGUE_ONLY'"
        sql += " ORDER BY key LIMIT ?"
        params.append(_bound(limit))
        return _rows(self.db.execute(sql, params))

    def fuels(self, investigation_id: str = "FLEX") -> list[str]:
        return [row[0] for row in self.db.execute(
            """SELECT DISTINCT fuel FROM experiments
               WHERE investigation_id=? AND validation_status='VALIDATED' AND fuel IS NOT NULL
               ORDER BY fuel""", (investigation_id,)
        )]

    def source(self, key: str) -> dict:
        row = self.db.execute("SELECT * FROM source_catalogue WHERE key=?", (key,)).fetchone()
        if row is None:
            raise ResearchError(f"unknown source: {key}")
        return dict(row)

    def source_evidence(self, key: str) -> list[dict]:
        self.source(key)  # Distinguish an unknown source from a known source with no admitted evidence.
        return _rows(self.db.execute(
            """SELECT source_location,summary,evidence_kind
               FROM catalogue_evidence WHERE catalogue_key=? ORDER BY id""", (key,)
        ))

    def experiments(
        self, *, investigation_id: str | None = None, fuel: str | None = None,
        test_query: str | None = None, oxygen_min: float | None = None,
        oxygen_max: float | None = None, pressure_min: float | None = None,
        pressure_max: float | None = None, measurement_variable: str = "burn_time_s",
        limit: int = 100, offset: int = 0,
    ) -> list[dict]:
        if measurement_variable not in VARIABLE_UNITS:
            raise ResearchError(f"unsupported measurement variable: {measurement_variable}")
        oxygen_min = _finite(oxygen_min, "oxygen_min")
        oxygen_max = _finite(oxygen_max, "oxygen_max")
        pressure_min = _finite(pressure_min, "pressure_min")
        pressure_max = _finite(pressure_max, "pressure_max")
        if oxygen_min is not None and oxygen_max is not None and oxygen_min > oxygen_max:
            raise ResearchError("oxygen_min exceeds oxygen_max")
        if pressure_min is not None and pressure_max is not None and pressure_min > pressure_max:
            raise ResearchError("pressure_min exceeds pressure_max")
        for value in (oxygen_min, oxygen_max):
            if value is not None and not 0 <= value <= 1:
                raise ResearchError("oxygen mole fraction must be within 0–1")
        sql = """
            SELECT e.id,e.investigation_id,e.original_test_id,e.fuel,e.test_date,e.gmt,
                   e.test_end,e.data_origin,e.validation_status,
                   o.numeric_value AS oxygen_mole_fraction,
                   p.numeric_value AS pressure_mmhg,
                   selected.original_value AS measurement_original,
                   selected.original_unit AS measurement_unit,
                   selected.numeric_value AS measurement_numeric,
                   selected.classification AS measurement_classification,
                   selected.uncertainty AS measurement_uncertainty,
                   selected.page AS measurement_page,
                   s.title AS source_title,s.source_url,s.rights AS source_rights
            FROM experiments e
            LEFT JOIN measurements o ON o.experiment_id=e.id AND o.variable='oxygen_mole_fraction'
            LEFT JOIN measurements p ON p.experiment_id=e.id AND p.variable='pressure_mmhg'
            LEFT JOIN measurements selected ON selected.experiment_id=e.id AND selected.variable=?
            JOIN sources s ON s.id=e.source_id
            WHERE e.validation_status='VALIDATED'
        """
        params: list = [measurement_variable]
        if investigation_id is not None:
            sql += " AND e.investigation_id=?"
            params.append(investigation_id)
        if fuel is not None:
            sql += " AND e.fuel=?"
            params.append(fuel)
        if test_query:
            # Treat user text literally, including SQL LIKE wildcard characters.
            literal = test_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql += " AND e.original_test_id LIKE ? ESCAPE '\\'"
            params.append(f"%{literal}%")
        for column, operator, value in (
            ("o.numeric_value", ">=", oxygen_min), ("o.numeric_value", "<=", oxygen_max),
            ("p.numeric_value", ">=", pressure_min), ("p.numeric_value", "<=", pressure_max),
        ):
            if value is not None:
                sql += f" AND {column}{operator}?"
                params.append(value)
        sql += " ORDER BY e.original_test_id LIMIT ? OFFSET ?"
        params.extend((_bound(limit), _nonnegative(offset, "offset")))
        return _rows(self.db.execute(sql, params))

    def experiment(self, experiment_id: str) -> dict:
        row = self.db.execute(
            """SELECT e.*,s.title AS source_title,s.source_url,s.status AS source_status,
                      s.rights AS source_rights
               FROM experiments e JOIN sources s ON s.id=e.source_id WHERE e.id=?""",
            (experiment_id,),
        ).fetchone()
        if row is None:
            raise ResearchError(f"unknown experiment: {experiment_id}")
        item = dict(row)
        item["measurements"] = self.measurements(experiment_id)
        return item

    def provenance(self, experiment_id: str) -> dict:
        row = self.db.execute(
            """SELECT e.id AS experiment_id,e.original_test_id,e.investigation_id,
                      e.data_origin,e.validation_status,s.title AS source_title,
                      s.source_url,s.sha256 AS source_sha256,s.status AS source_status,
                      s.rights AS source_rights,
                      min(m.page) AS first_pdf_page,max(m.page) AS last_pdf_page
               FROM experiments e JOIN sources s ON s.id=e.source_id
               JOIN measurements m ON m.experiment_id=e.id
               WHERE e.id=? GROUP BY e.id""", (experiment_id,)
        ).fetchone()
        if row is None:
            raise ResearchError(f"unknown experiment: {experiment_id}")
        return dict(row)

    def measurements(self, experiment_id: str) -> list[dict]:
        return _rows(self.db.execute(
            """SELECT m.id,m.variable,m.original_value,m.original_unit,m.numeric_value,
                      m.classification,m.uncertainty,m.page,t.topic_id,
                      s.title AS source_title,s.source_url,s.rights AS source_rights
               FROM measurements m JOIN measurement_topics t ON t.measurement_id=m.id
               JOIN sources s ON s.id=m.source_id
               WHERE m.experiment_id=? ORDER BY m.id""",
            (experiment_id,),
        ))

    def passages(
        self, query: str, *, investigation_id: str | None = None,
        topic_id: str | None = None, limit: int = 20,
    ) -> list[dict]:
        terms = re.findall(r"[\w]+", query, re.UNICODE)
        if not terms or len(terms) > 12 or len(query) > 200:
            raise ResearchError("search requires 1–12 plain terms and at most 200 characters")
        # Quoted FTS terms prevent callers from injecting FTS operators or syntax.
        expression = " AND ".join(f'"{term}"' for term in terms)
        sql = """
            SELECT p.id,p.page,substr(p.text,1,1800) AS excerpt,
                   s.title AS source_title,s.source_url,s.investigation_id,
                   bm25(passages_fts) AS rank
            FROM passages_fts JOIN passages p ON p.id=passages_fts.rowid
            JOIN sources s ON s.id=p.source_id
            WHERE passages_fts MATCH ? AND s.status='VERIFIED'
        """
        params: list = [expression]
        if investigation_id is not None:
            sql += " AND s.investigation_id=?"
            params.append(investigation_id)
        if topic_id is not None:
            sql += " AND EXISTS (SELECT 1 FROM passage_topics t WHERE t.passage_id=p.id AND t.topic_id=?)"
            params.append(topic_id)
        sql += " ORDER BY rank,p.id LIMIT ?"
        params.append(_bound(limit, 100))
        return _rows(self.db.execute(sql, params))

    def measurement_frame(self, variable: str, *, investigation_id: str = "FLEX",
                          fuel: str | None = None) -> pd.DataFrame:
        if variable not in VARIABLE_UNITS:
            raise ResearchError(f"unsupported measurement variable: {variable}")
        sql = """
            SELECT e.id AS experiment_id,e.original_test_id,e.fuel,e.test_end,
                   m.numeric_value,m.original_value,m.original_unit,
                   m.classification,m.uncertainty,m.page,
                   s.title AS source_title,s.source_url
            FROM measurements m JOIN experiments e ON e.id=m.experiment_id
            JOIN sources s ON s.id=m.source_id
            WHERE m.variable=? AND e.investigation_id=? AND e.validation_status='VALIDATED'
        """
        params: list = [variable, investigation_id]
        if fuel is not None:
            sql += " AND e.fuel=?"
            params.append(fuel)
        sql += " ORDER BY e.original_test_id"
        frame = pd.DataFrame.from_records(_rows(self.db.execute(sql, params)))
        if not frame.empty and set(frame["original_unit"]) != {VARIABLE_UNITS[variable]}:
            raise ResearchError(f"mixed or unexpected original units for {variable}")
        return frame

    def describe_measurement(self, variable: str, *, investigation_id: str = "FLEX",
                             fuel: str | None = None) -> dict:
        frame = self.measurement_frame(variable, investigation_id=investigation_id, fuel=fuel)
        if frame.empty:
            return {"variable": variable, "unit": VARIABLE_UNITS[variable],
                    "count": 0, "missing": 0, "mean": None, "minimum": None, "maximum": None}
        values = frame["numeric_value"].to_numpy(dtype=float)
        valid = values[np.isfinite(values)]
        return {
            "variable": variable, "unit": VARIABLE_UNITS[variable],
            "count": int(valid.size), "missing": int(values.size - valid.size),
            "mean": float(np.mean(valid)) if valid.size else None,
            "minimum": float(np.min(valid)) if valid.size else None,
            "maximum": float(np.max(valid)) if valid.size else None,
            "derived_from": "descriptive aggregation of NASA_REPORT_EXTRACTED values",
        }


def validate_database(store: ResearchStore) -> dict:
    """Check scientific invariants without altering the source corpus."""
    db = store.db
    problems: list[str] = []
    if db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
        problems.append("SQLite integrity check failed")
    if db.execute("PRAGMA foreign_key_check").fetchall():
        problems.append("foreign-key violations")
    for table, expected in (("experiments", 273), ("measurements", 2457), ("passages", 329)):
        if db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] != expected:
            problems.append(f"unexpected {table} count")
    if db.execute("SELECT count(*) FROM passages_fts").fetchone()[0] != 329:
        problems.append("FTS5 index count differs from passages")
    if db.execute("SELECT count(*) FROM experiments WHERE data_origin!='NASA_REPORT_EXTRACTED' OR validation_status!='VALIDATED'").fetchone()[0]:
        problems.append("unapproved experiment origin or status")
    if db.execute("SELECT count(*) FROM measurements WHERE classification='UNAVAILABLE' AND numeric_value IS NOT NULL").fetchone()[0]:
        problems.append("missing-value marker has a numeric value")
    if db.execute("SELECT count(*) FROM measurements WHERE classification!='UNAVAILABLE' AND numeric_value IS NULL").fetchone()[0]:
        problems.append("numeric measurement has no numeric value")
    if db.execute("SELECT count(DISTINCT passage_id) FROM passage_topics").fetchone()[0] != 329:
        problems.append("unclassified passages")
    if db.execute("SELECT count(*) FROM measurement_topics").fetchone()[0] != 2457:
        problems.append("unclassified measurements")
    if db.execute("""
        SELECT count(*) FROM measurements m JOIN experiments e ON e.id=m.experiment_id
        WHERE m.source_id<>e.source_id
    """).fetchone()[0]:
        problems.append("measurement source differs from experiment source")
    if db.execute("""
        SELECT count(*) FROM measurements m JOIN sources s ON s.id=m.source_id
        WHERE m.page<1 OR m.page>s.pages
    """).fetchone()[0]:
        problems.append("measurement page outside source document")
    for variable, unit in VARIABLE_UNITS.items():
        if db.execute("SELECT count(*) FROM measurements WHERE variable=? AND original_unit<>?", (variable, unit)).fetchone()[0]:
            problems.append(f"unit mismatch: {variable}")
    if db.execute("""
        SELECT count(*) FROM measurements
        WHERE variable LIKE '%mole_fraction' AND numeric_value IS NOT NULL
          AND (numeric_value<0 OR numeric_value>1)
    """).fetchone()[0]:
        problems.append("gas mole fraction outside 0–1")
    if db.execute("""
        SELECT count(*) FROM measurements
        WHERE variable IN ('pressure_mmhg','initial_diameter_mm','burning_rate_mm2_s','burn_time_s')
          AND numeric_value IS NOT NULL AND numeric_value<=0
    """).fetchone()[0]:
        problems.append("nonpositive pressure, initial size, rate, or duration")
    if db.execute("""
        SELECT count(*) FROM measurements
        WHERE variable='visible_extinction_diameter_mm' AND numeric_value<0
    """).fetchone()[0]:
        problems.append("negative visible-extinction diameter")
    if db.execute("""
        SELECT count(*) FROM (
            SELECT experiment_id,SUM(numeric_value) AS total
            FROM measurements
            WHERE variable IN ('oxygen_mole_fraction','nitrogen_mole_fraction',
                               'carbon_dioxide_mole_fraction','helium_mole_fraction')
            GROUP BY experiment_id HAVING ABS(total-1)>0.031
        )
    """).fetchone()[0]:
        problems.append("atmospheric mole fractions disagree beyond report rounding")
    if db.execute("""
        SELECT count(*) FROM catalogue_evidence e JOIN source_catalogue c
          ON c.key=e.catalogue_key
        WHERE c.rights_status<>'CC0-1.0' OR c.verification_status<>'VERIFIED_METADATA'
    """).fetchone()[0]:
        problems.append("unapproved catalogue evidence")
    if problems:
        raise ResearchError("; ".join(problems))
    return {"experiments": 273, "measurements": 2457, "passages": 329,
            "sources": db.execute("SELECT count(*) FROM source_catalogue").fetchone()[0],
            "status": "VALIDATED_SUBSET"}
