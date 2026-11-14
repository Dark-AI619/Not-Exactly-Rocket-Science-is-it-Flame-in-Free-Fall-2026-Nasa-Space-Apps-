# Phase 3D — scientific comparisons

Checked 2026-11-15. This checkpoint connects Compare & Analyze to admitted FLEX Table IX measurements. It remains on the `phase3-integration` development branch and does not publish new functionality to Streamlit Community Cloud.

## Implementation

- `backend/analysis.py` builds a source-traceable Pandas comparison from validated FLEX experiments and their original measurement records. It filters fuel, oxygen mole fraction, pressure and selected original test IDs. It validates variables and units, preserves original tokens and classifications, and keeps missing cells in the inspection table while omitting incomplete pairs from charts.
- `app.py` offers measurement axes and condition filters, a Plotly scatter of complete pairs, a descriptive fuel distribution, counts for unavailable values, a condition-variation warning, and a table of original values, units, source classifications, uncertainties, PDF pages and NASA source URL.
- `requirements.txt` adds Plotly; `tests/test_analysis.py` checks missing-pair arithmetic, original values and pages for FLEX test 130, fuel/oxygen scoping, source classification and invalid comparisons.

## Verified numerical scope

The default initial-diameter versus burn-duration view starts with 273 validated FLEX tests. It plots 260 complete pairs; 11 lack an initial diameter, six lack a burn duration and 13 lack at least one axis value. Four tests lack both. The displayed source classifications are `MEASURED`, `DERIVED` and `UNAVAILABLE` as stored in the transcription. The database has no cell-level uncertainty entries, so the interface draws no uncertainty bars and labels them as unreported. No data are imputed or converted, and no causal fit is drawn.

## Checks

`python -m pytest tests/test_analysis.py tests/test_backend.py tests/test_phase3a.py -q` passed **23 tests**. `python -m py_compile app.py backend/analysis.py` and `git diff --check` passed. A local Streamlit session on port 8506 was inspected in a browser: the default scatter and fuel box plot rendered with original `mm` and `s` axis labels; selecting Heptane changed the view to 118 tests and 108 complete default pairs; changing the vertical axis to burning-rate constant updated missing counts. The browser reported two Plotly charts, no Streamlit exception, and no horizontal overflow at 1280 px width.

## Scientific limits

The views describe the validated report-extracted subset, not the full FLEX investigation or live telemetry. Fuels, oxygen composition and atmospheric pressures vary across the default selection; the page discloses their ranges before interpretation. A box plot is a derived descriptive summary of filtered rows and does not appear in the NASA report. Report outcomes are shown as categories, not inferred from chart position. The source link opens the NASA NTRS report record, while each trace row shows its PDF page. BASS-II, Saffire, SAME-R and SPICE still have no admitted numerical experiments. No spacecraft safety certification or universal causal claim is made.

**Checkpoint: 3D complete on the development branch. Await explicit approval before 3E.**
