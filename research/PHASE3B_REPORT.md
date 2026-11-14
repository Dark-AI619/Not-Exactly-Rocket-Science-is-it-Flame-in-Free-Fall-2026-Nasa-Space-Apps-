# Phase 3B — scientific backend and database services

Checked 2026-11-14. This milestone provides Python services independent of Streamlit. It does not activate any dashboard data controls; Research Explorer and Research Records integration belongs to 3C.

## Services

`backend.ResearchStore` opens `data/flame_research.db.gz` as an in-memory SQLite snapshot and sets `query_only`. It also supports an uncompressed SQLite file opened with `mode=ro`. Its parameterized methods provide:

- Research domains, topics, investigation coverage, source catalogue, and admitted source summaries.
- Source identity, verification and rights status.
- Validated experiment search with literal test-ID matching, fuel, oxygen mole-fraction and pressure filters, bounded pagination.
- Complete experiment detail, original measurement tokens, original units, classification, uncertainty field, PDF page, source URL, and provenance hash.
- Bounded FTS5 page-passage search with optional investigation and topic scope. Search terms are quoted before use in `MATCH`.
- Pandas measurement frames and NumPy descriptive summaries. The summary is explicitly derived; missing values are counted separately and no unit conversion or imputation occurs.

`validate_database` checks SQLite integrity and foreign keys, corpus counts, experiment origin/status, FTS and topic coverage, measurement/source linkage, PDF page bounds, original units, missing-value markers, basic physical ranges, gas-fraction rounding tolerance, and rights status of newly admitted objective summaries. It returns a `VALIDATED_SUBSET` status for the current FLEX report transcription.

## Restricted SQL

`backend.RestrictedSQL` constructs a disposable in-memory projection containing only approved experiment, measurement, source, passage, topic and domain columns. It omits local file paths and raw database schema tables. The projection is set to `query_only`; an SQLite authorizer permits only reads of its six approved tables, SELECT operations, and a small allowlist of aggregate/scalar functions.

Each SQL request gets a fresh projection. One statement is executed with optional bound parameters. The interface caps SQL length at 4,000 characters, rows at 500, columns at 40, string length at 8,192 bytes, result text at 250,000 characters, and work at 100,000 VM steps or one second by default. It rejects updates, deletion, schema changes, PRAGMA, ATTACH, access to hidden tables, unsafe functions and recursive queries. The authoritative archive cannot be changed by this service.

The SQL service is a backend capability only. Streamlit will expose it in 3C after the user-facing query flow is tested.

## Verification

`python -m pytest tests/test_backend.py tests/test_phase3a.py -q` passed **20 tests**. Tests cover source and provenance lookup, category and investigation coverage, real FLEX filters, scoped FTS5 results, original units and unavailable cells, numerical summaries, bounded SQL results, ten unsafe SQL attempts, and archive immutability. `python -m py_compile backend/*.py` and `git diff --check` also pass.

The archive remains a subset: 273 validated FLEX experiments, 2,457 original measurement cells and 329 PDF page passages. BASS-II has 20 documentary passages and no admitted numerical rows. Saffire, SAME-R and SPICE have no admitted numerical rows. No inferred outcomes, synthetic measurements, paid API integration, or frontend connection was introduced.

## Interface contract for 3C

The next milestone may call these services from the existing six-page app. The backend returns plain dictionaries, Pandas frames and a `QueryResult` with explicit truncation. Missing or unknown records raise `ResearchError`; unsafe SQL raises `QueryRejected`. Source-page and provenance fields are available for display beside every measurement.

**Checkpoint: 3B complete. Await explicit approval before 3C.**
