# Flame in Freefall

An independent NASA Space Apps Challenge 2026 project by **Not Exactly Rocket Science, Is It?!**. The six-section Streamlit interface is connected to verified research in staged development checkpoints. Phase 3 provides real FLEX records, descriptive comparisons and source retrieval. Phase 4C adds optional, source-checked Groq explanations to Assistant and Solution Lab on the development branch. The public deployment remains on the earlier Phase 3B version. No physical simulation or sample measurements are invented.

## Run locally

Use Python 3.12. Install `requirements.txt`, then run `streamlit run app.py`. No API key is required.

## Research status

Phase 1 produced a separately preserved, validated transcription subset of FLEX Table IX from [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456). Checkpoint 3C reads that subset: 273 validated report-extracted tests and 2,457 original measurement cells. The catalogue includes 329 searchable PDF page passages and 23 sources. BASS-II, SAME-R, and Saffire have no admitted numerical experiment rows. NASA PSI investigation pages are research sources, including [FLEX PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69). Original units, source pages, rights, and uncertainty are retained.

## Artwork and attribution

The project owner supplied two images. The astronaut and NASA International Space Apps Challenge artwork appears only in the Research Explorer hero, with its branding preserved. The flame-over-Earth artwork appears in View Effect as a conceptual illustration, not experimental footage. Their use does not imply that NASA operates or endorses this independent dashboard.

## AI assistance

ChatGPT/Codex assisted with Phase 1 data preparation and Phase 2–4 code and design. Generated Python files carry the required co-author comment. Without an owner-configured Groq key, Assistant and Solution Lab provide deterministic source retrieval; no visitor key is requested.

## Phase 3A research audit

The research catalogue migration and audit are documented in `research/PHASE3A_REPORT.md`. The repository includes a compressed, topic-indexed copy of the validated Phase 1 database at `data/flame_research.db.gz`.

## Phase 3B backend

The standalone `backend` package provides read-only scientific data services, integrity validation, Pandas/NumPy descriptive summaries, FTS5 passage search, and a restricted SQL interface over approved projections. See `research/PHASE3B_REPORT.md` for its scope and limits. Run `python -m pytest tests/test_backend.py tests/test_phase3a.py -q` with `requirements.txt` and `requirements-dev.txt` installed.

## Phase 3C research pages

Research Explorer browses domains, investigations, topics, source records, and PDF passage hits. Research Records filters the admitted FLEX Table IX subset, displays original measured tokens and units, shows missing cells and source-page provenance, and permits bounded read-only queries with CSV export. See `research/PHASE3C_REPORT.md` for verification and limitations. These changes are committed to a development branch; Phase 3 does not publish new functionality to the public Streamlit demo.

## Phase 3D scientific comparisons

Compare & Analyze filters admitted FLEX tests by fuel, oxygen mole fraction, pressure and original test ID. It plots only pairs with both requested values, retains missing and source-classification status, shows original axis units, and includes a source-trace table. The scatter and fuel distribution are descriptive views of the selected subset; changing experimental conditions are flagged. See `research/PHASE3D_REPORT.md` for numerical checks and limits. Plotly is required in addition to the existing runtime packages.

## Phase 3E evidence retrieval

`backend/retrieval.py` routes a question by intent, domain, investigation aliases and topic synonyms, then retrieves a bounded set of indexed PDF passages, approved objective summaries or exact validated FLEX test measurements. Assistant shows the deterministic evidence packet and exact citations; Solution Lab separates source observations from design questions; View Effect keeps conceptual artwork distinct from verified test conditions. See `research/PHASE3E_REPORT.md` for tests and limitations, and `research/ADMISSION_ARCHITECTURE.md` for the future reviewed-source workflow. No public Add Research control or unattended source admission is enabled.

## Phase 3F local readiness

The full local integration audit is documented in `research/PHASE3F_READINESS.md`. All 30 automated tests pass and all six sections load locally. The integrated backend is usable for the admitted FLEX report subset and source-linked documentary retrieval. Mir fire facts, BASS-II numerical comparisons and authentic experiment footage remain outside the approved corpus; the interface reports those gaps rather than filling them from unreviewed material. The development branch is not the public Streamlit deployment.

## Phase 4A optional Groq configuration

The official Groq SDK is an optional generation boundary in `backend/groq_adapter.py`. The existing deterministic evidence mode works with no API key. Copy `.env.example` values into private environment variables or `.streamlit/secrets.toml` (never commit that file). `GROQ_API_KEY` is the only secret. `GROQ_MODEL` defaults to `qwen/qwen3.8-27b`; confirm that the chosen model is still available on the owner's free-tier account before any live request. `GROQ_MAX_OUTPUT_TOKENS`, `GROQ_REQUEST_TIMEOUT` and `AI_SESSION_REQUEST_LIMIT` have bounded defaults. See `research/PHASE4A_REPORT.md` for the offline mock results and limits.

## Phase 4B grounded answer service

`backend/grounded.py` takes the existing category-routed evidence packet, supplies at most six admitted items within an 11,000-character context, and requests short citation-tagged JSON claims through the optional Groq adapter. It checks citation IDs, source vocabulary and numbers against cited evidence before exposing any generated claim. Unsupported answers and provider failures return the original deterministic packet. See `research/PHASE4B_REPORT.md` for offline tests and the limits of heuristic claim verification.

## Phase 4C Assistant and Solution Lab

The development-branch Assistant and Solution Lab now use the same `research_turn` service, optional Groq adapter, citation checks and per-session request budget. Assistant retains a short conversation and sends at most two prior questions as phrasing context; only current retrieved evidence supports claims. Solution Lab separates verified observations, checked interpretation, conditional engineering directions, limitations and citations. Missing keys, unsupported questions and provider errors retain the verified evidence view. See `research/PHASE4C_REPORT.md` for tests and remaining limits. No live Groq request or public deployment occurred in this checkpoint.
