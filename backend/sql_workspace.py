# Co-authored with ChatGPT
"""A restricted, read-only SQL interface over approved research projections."""
from __future__ import annotations

import sqlite3
import time
from dataclasses import dataclass

from .store import ResearchStore, ResearchError

APPROVED_TABLES = {
    "experiment_records", "measurement_records", "source_records",
    "research_passages", "research_topics", "research_domains",
}
SAFE_FUNCTIONS = {
    "abs", "avg", "coalesce", "count", "ifnull", "length", "lower",
    "max", "min", "nullif", "round", "sum", "trim", "upper",
}


class QueryRejected(ResearchError):
    """SQL was unsafe, exceeded a resource limit, or referenced hidden data."""


@dataclass(frozen=True)
class QueryResult:
    columns: tuple[str, ...]
    rows: tuple[dict, ...]
    truncated: bool


class RestrictedSQL:
    """Build disposable projections, then authorize only bounded reads."""

    def __init__(self, store: ResearchStore, *, max_rows: int = 500,
                 timeout_seconds: float = 1.0, max_vm_steps: int = 100_000):
        if not 1 <= max_rows <= 500:
            raise ValueError("max_rows must be 1–500")
        if timeout_seconds <= 0 or max_vm_steps <= 0:
            raise ValueError("execution limits must be positive")
        self.store = store
        self.max_rows = max_rows
        self.timeout_seconds = timeout_seconds
        self.max_vm_steps = max_vm_steps

    def _projection(self) -> sqlite3.Connection:
        db = sqlite3.connect(":memory:")
        db.row_factory = sqlite3.Row
        db.executescript("""
            CREATE TABLE experiment_records(
                id TEXT, investigation_id TEXT, original_test_id TEXT, fuel TEXT,
                test_date TEXT, gmt TEXT, test_end TEXT, data_origin TEXT,
                validation_status TEXT, source_title TEXT, source_url TEXT
            );
            CREATE TABLE measurement_records(
                experiment_id TEXT, original_test_id TEXT, variable TEXT,
                original_value TEXT, original_unit TEXT, numeric_value REAL,
                classification TEXT, uncertainty TEXT, pdf_page INTEGER,
                source_title TEXT, source_url TEXT
            );
            CREATE TABLE source_records(
                source_key TEXT, title TEXT, publisher TEXT, source_url TEXT,
                identifier TEXT, domain_id TEXT, investigation_id TEXT,
                primary_topic_id TEXT, source_type TEXT, verification_status TEXT,
                rights_status TEXT, admission_status TEXT
            );
            CREATE TABLE research_passages(
                passage_id INTEGER, investigation_id TEXT, pdf_page INTEGER,
                source_title TEXT, source_url TEXT, passage_text TEXT
            );
            CREATE TABLE research_topics(id TEXT, domain_id TEXT, label TEXT);
            CREATE TABLE research_domains(id TEXT, label TEXT);
        """)
        src = self.store.db
        db.executemany(
            "INSERT INTO experiment_records VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            src.execute("""
                SELECT e.id,e.investigation_id,e.original_test_id,e.fuel,
                       e.test_date,e.gmt,e.test_end,e.data_origin,e.validation_status,
                       s.title,s.source_url
                FROM experiments e JOIN sources s ON s.id=e.source_id
                WHERE e.validation_status='VALIDATED'
            """).fetchall(),
        )
        db.executemany(
            "INSERT INTO measurement_records VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            src.execute("""
                SELECT m.experiment_id,e.original_test_id,m.variable,m.original_value,
                       m.original_unit,m.numeric_value,m.classification,m.uncertainty,
                       m.page,s.title,s.source_url
                FROM measurements m JOIN experiments e ON e.id=m.experiment_id
                JOIN sources s ON s.id=m.source_id
                WHERE e.validation_status='VALIDATED'
            """).fetchall(),
        )
        db.executemany(
            "INSERT INTO source_records VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            src.execute("""
                SELECT key,title,publisher,url,identifier,domain_id,
                       investigation_id,primary_topic_id,source_type,
                       verification_status,rights_status,admission_status
                FROM source_catalogue
            """).fetchall(),
        )
        db.executemany(
            "INSERT INTO research_passages VALUES (?,?,?,?,?,?)",
            src.execute("""
                SELECT p.id,s.investigation_id,p.page,s.title,s.source_url,
                       substr(p.text,1,1800)
                FROM passages p JOIN sources s ON s.id=p.source_id
                WHERE s.status='VERIFIED'
            """).fetchall(),
        )
        db.executemany(
            "INSERT INTO research_topics VALUES (?,?,?)",
            src.execute("SELECT id,domain_id,label FROM research_topics").fetchall(),
        )
        db.executemany(
            "INSERT INTO research_domains VALUES (?,?)",
            src.execute("SELECT id,label FROM research_domains").fetchall(),
        )
        db.commit()
        db.execute("PRAGMA query_only=ON")
        db.setlimit(sqlite3.SQLITE_LIMIT_SQL_LENGTH, 4_000)
        db.setlimit(sqlite3.SQLITE_LIMIT_COLUMN, 40)
        db.setlimit(sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 30)
        db.setlimit(sqlite3.SQLITE_LIMIT_COMPOUND_SELECT, 5)
        db.setlimit(sqlite3.SQLITE_LIMIT_VARIABLE_NUMBER, 50)
        db.setlimit(sqlite3.SQLITE_LIMIT_LENGTH, 8_192)
        return db

    @staticmethod
    def _authorize(action: int, arg1: str | None, arg2: str | None,
                   _database: str | None, _source: str | None) -> int:
        if action == sqlite3.SQLITE_SELECT:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_READ and arg1 in APPROVED_TABLES:
            return sqlite3.SQLITE_OK
        if action == sqlite3.SQLITE_FUNCTION and (arg2 or "").lower() in SAFE_FUNCTIONS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    def execute(self, sql: str, parameters: tuple | dict = ()) -> QueryResult:
        if not isinstance(sql, str) or not sql.strip() or len(sql) > 4_000:
            raise QueryRejected("SQL must contain one statement of at most 4,000 characters")
        if not isinstance(parameters, (tuple, dict)):
            raise QueryRejected("parameters must be a tuple or mapping")
        db = self._projection()
        start = time.monotonic()
        steps = 0

        def progress() -> int:
            nonlocal steps
            steps += 1_000
            return int(steps > self.max_vm_steps or
                       time.monotonic() - start > self.timeout_seconds)

        try:
            db.set_authorizer(self._authorize)
            db.set_progress_handler(progress, 1_000)
            cursor = db.execute(sql, parameters)
            if cursor.description is None:
                raise QueryRejected("Only read-only result queries are permitted")
            columns = tuple(col[0] for col in cursor.description)
            if len(columns) > 40:
                raise QueryRejected("Too many output columns")
            if len(set(columns)) != len(columns):
                raise QueryRejected("Duplicate output names; use explicit AS aliases")
            fetched = cursor.fetchmany(self.max_rows + 1)
            rows: list[dict] = []
            size = 0
            truncated = len(fetched) > self.max_rows
            for raw in fetched[:self.max_rows]:
                row = dict(zip(columns, raw))
                size += sum(len(str(value)) for value in row.values() if value is not None)
                if size > 250_000:
                    truncated = True
                    break
                rows.append(row)
            return QueryResult(
                columns, tuple(rows), truncated,
            )
        except sqlite3.Error as exc:
            raise QueryRejected(f"Query rejected: {exc}") from exc
        finally:
            db.close()
