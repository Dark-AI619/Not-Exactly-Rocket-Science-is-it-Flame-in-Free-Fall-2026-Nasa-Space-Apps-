# Phase 4E local release readiness — 15 November 2026

## Scope and changes

This is a tested **development-branch release candidate**, not a public deployment. The approved six-workspace graphite/cyan/orange design and both supplied artworks are retained. The shared Streamlit evidence cache was removed because its keys contained visitor questions; evidence is now retrieved independently per request. The AI caption now accurately describes automated citation/value checks as checks, rather than a guarantee of scientific truth. No research rows, source admissions, or scientific values changed.

## Scientific and security state

- SQLite `integrity_check`: `ok`; foreign-key violations: `0`; ordinary connection `query_only=1`.
- Corpus: 273 validated FLEX report-extracted experiments, 2,457 original measurement cells, 329 PDF passages, 10 admitted documentary notes, 25 catalogued sources.
- Restricted SQL uses an approved read-only projection, an SQLite authorizer, a 500-row cap, VM/time limits, and output size limits. SQL security tests pass.
- Evidence retrieval is category routed and bounded. The grounded answer service checks source IDs and textual/numerical tokens, then falls back to source evidence on failure. These checks are heuristic and do not prove semantic truth.
- The optional Groq path has bounded output tokens (default 600; allowed 64–2,048), 20-second default request timeout (allowed 1–60), up to three attempts, short retry waits, `Retry-After` handling, and an eight-request default per-session limit (allowed 1–50). Missing key, rate limit, and provider errors show evidence-only status. All provider tests used mocks; **no live Groq request was made**.
- The per-session limit does not cap aggregate use across visitors. A public shared free quota would need server-side global accounting, rate limits tied to a trustworthy identity or abuse signal, and operational monitoring. Those controls require infrastructure beyond this Streamlit-only release candidate. No paid billing is enabled.

## Measured local performance

`python scripts/benchmark_release.py` (Python 3.12, Windows, local packaged corpus; medians of 10 runs except chart at 5):

| Operation | Median |
| --- | ---: |
| SQLite archive load | 4.69 ms |
| FLEX category retrieval | 1.20 ms |
| Mir historical retrieval | 0.65 ms |
| FTS5 passage search | 0.43 ms |
| Restricted SQL aggregate, including projection build | 42.58 ms |
| Comparison dataframe and 260-point Plotly chart construction | 144.48 ms |

Python `tracemalloc` peak during that run: 23.24 MiB (excludes native allocations and is not process RSS). A separate local Streamlit launch reached `/_stcore/health` HTTP 200 (`ok`) in 1,951 ms. A browser visit initialized the six workspaces. These are local observations, not hosted performance guarantees. Mocked request outcomes, retries, and fallback are tested in `tests/test_groq_adapter.py`, `tests/test_grounded.py`, and `tests/test_research_session.py`; no network latency was measured.

## Verification

- `python -m pytest tests -q`: 53 passed. The suite covers numerical comparison and missing values, DB admission/integrity, SQL restrictions, citation validation, retrieval routing, missing-key fallback, request budgets, mocked Groq rate limits and retries.
- `python -m compileall -q app.py backend scripts migrations tests`: passed.
- `git diff --check`: passed.
- Local Streamlit health: HTTP 200, body `ok`.
- Browser: navigated all six pages; each loaded its correct heading with no visible exception. Research Explorer and View Effect showed their intended images. The View Effect artwork retained its natural proportions. At 390 px viewport, Research Explorer had document scroll width 390 px and no horizontal page overflow. Sidebar navigation collapses on narrow screens.

## Deployment preparation — manual checklist, no deployment performed

1. Review the development-branch diff and this report. Keep `main` and the public Streamlit app unchanged until the owner approves a later release.
2. Use Python 3.12 and install `requirements.txt`. All required images and the compressed database are committed. No absolute Windows paths are required at runtime.
3. Launch with `python -m streamlit run app.py`; confirm `/_stcore/health` and the six sections. The app needs no secret for evidence-only use.
4. If optional generation is desired, set `GROQ_API_KEY` in private Streamlit secrets or the deployment environment. Set `GROQ_MODEL`, `GROQ_MAX_OUTPUT_TOKENS`, `GROQ_REQUEST_TIMEOUT`, and `AI_SESSION_REQUEST_LIMIT` only as needed. Verify the chosen model/account availability and make an explicitly authorized live test before claiming live integration.
5. Before public AI use, add a global quota/abuse control appropriate to the owner's free account. Per-session control alone does not prevent quota exhaustion by many visitors.
6. Recheck source rights and image attribution before release. Do not represent report-extracted FLEX rows as PSI telemetry, the artwork as test footage, or catalogue-only sources as measured experiments.

## Remaining limitations

The scientific scope is the verified FLEX Table IX subset, with only documentary evidence for the other listed investigations. Original PSI telemetry is not present. Groq responses have not been live tested. The source-checker may reject sound paraphrases or miss semantic contradictions; users must inspect citations. The narrow-screen check covered one phone width, not a device matrix. The public deployment remains on its earlier branch/version.

**STOP after 4E.**
