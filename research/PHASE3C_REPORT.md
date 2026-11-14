# Phase 3C — Research Explorer and Research Records

Checked 2026-11-15. This checkpoint connects the existing Streamlit research pages to the verified SQLite snapshot through the Phase 3B read-only services. It does not connect charts, AI answers, Solution Lab, or View Effect to scientific calculations.

## Implementation

- `app.py`: Explorer now shows verified corpus counts, research-domain/topic/investigation filters, numerical versus documentary availability, source catalogue and provenance links, and scoped FTS5 PDF passage search. Selecting FLEX can open its experiment records directly.
- `app.py`: Records now filters the validated FLEX subset by original test ID, fuel, oxygen mole fraction, pressure, and displayed measurement. It shows original tokens, original units, source PDF page, reported outcome, missing-value and approximate-value status, measurement uncertainty, source rights and hash. CSV export includes all filtered rows when the source's recorded rights permit use.
- `app.py`: The SQL editor calls `RestrictedSQL` from Phase 3B and displays bounded read-only results or explicit rejection messages. It provides a CSV download for approved result rows.
- `backend/store.py`: Source-topic filtering includes linked report passages and measurements. Experiment search can join a selected original measurement for table display, with its classification, unit and PDF page. The backend provides the admitted fuel list.
- `tests/test_backend.py`: Added integration-facing assertions for filtered source-topic coverage, admitted fuels, and original measurement projection.

## Verified scope

The database contains 273 validated FLEX Table IX tests, 2,457 original measurement cells, 329 PDF page passages and 23 catalogued sources. The numerical data origin is `NASA_REPORT_EXTRACTED`, not PSI raw telemetry. BASS-II, SAME-R, Saffire and SPICE have no admitted numerical rows; the Records page says so explicitly. Report pages are displayed as PDF page numbers and printed page numbers, with a link to the NASA NTRS source record.

## Checks

`python -m py_compile app.py backend/store.py` and `python -m pytest tests/test_backend.py tests/test_phase3a.py -q` passed (20 tests). A local Streamlit session on port 8505 was inspected through the browser: Explorer displayed counts and investigation/source controls; selecting FLEX and clicking **Open FLEX experiments** reached Records; `FLEX–130` returned one Heptane record with reported oxygen fraction 0.17, pressure 537.2 mmHg and PDF page 29; the experiment inspector displayed its original measurements and source provenance. An approved `SELECT` returned real FLEX rows, while `DELETE FROM experiment_records` was rejected as `not authorized`. Selecting BASS-II showed the explicit numerical-data absence message and documentary sources. The desktop Records layout was visually inspected at 1280 × 720 with no horizontal overflow in the initial viewport.

## Limits

The source link opens the NASA report record, not an in-browser PDF page anchor. No complete PSI telemetry archive is claimed. Only the admitted FLEX subset supports numerical filtering; source-search results represent document passages rather than new experimental rows. Approximate values are labeled when the original token has an approximation prefix; unavailable cells remain unavailable. The public Streamlit deployment is intentionally left at its earlier milestone, as the Phase 3 instructions reserve production publishing for a later step.

**Checkpoint: 3C complete on a development branch. Await explicit approval before 3D.**
