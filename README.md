# Flame in Freefall

An independent NASA Space Apps Challenge 2026 project by **Not Exactly Rocket Science, Is It?!**. The six-section Streamlit interface is connected to verified research in staged development checkpoints. Phase 3 provides real FLEX records, descriptive comparisons and source retrieval. Phase 4C adds optional, source-checked Groq explanations to Assistant and Solution Lab on the development branch. The public deployment remains on the earlier Phase 3B version. No physical simulation or sample measurements are invented.

## Run locally

Use Python 3.12. Install `requirements.txt`, then run `streamlit run app.py`. No API key is required.

For a clean checkout:

```sh
python -m venv .venv
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app reads `data/flame_research.db.gz` and both images in `assets/` relative to the repository. The database is opened with SQLite `query_only=ON`; ordinary visitors cannot change it. The local health endpoint is `/_stcore/health`.

## Release candidate and free-tier limits

The Phase 4E release candidate is on `phase3-integration`. It has **not** been merged into `main` or deployed. See `research/PHASE4E_REPORT.md` for the local checks and manual deployment checklist.

The app works in evidence-only mode without secrets. An owner may set `GROQ_API_KEY` privately for optional generation. The non-secret settings in `.env.example` control model, maximum output tokens, timeout and per-session request limit. Do not commit `.env`, `.streamlit/secrets.toml`, or a live key. The per-session limit cannot protect one shared free quota from many separate visitors; public launch would need a separate global budget or abuse-control service. Free inference availability and model access can change. No paid billing is required or enabled by this repository.

Phase 5 Pass A adds a connected path from a verified FLEX test through its measurements, descriptive comparison, source-linked question, Solution Lab, and test-aware visual context. See `research/PHASE5A_REPORT.md` for that checkpoint's local browser journey.

Phase 5 Pass B adds a limited D-squared liquid-droplet model to View Effect. Visitors can play, pause, and reset a calculated diameter curve with illustrative sliders or load compatible, validated FLEX D₀ and K values. Report outcomes and burn durations remain separate from calculated values. See `research/PHASE5B_REPORT.md` for scientific assumptions, source checks, and browser verification. Final responsive and release checks remain for Pass C.

## Research status

Phase 1 produced a separately preserved, validated transcription subset of FLEX Table IX from [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456). Checkpoint 3C reads that subset: 273 validated report-extracted tests and 2,457 original measurement cells. The catalogue now includes 329 searchable PDF page passages, 10 short source-linked documentary notes and 25 sources. BASS-II, SAME-R, and Saffire have no admitted numerical experiment rows. NASA PSI investigation pages are research sources, including [FLEX PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69). Original units, source pages, rights, and uncertainty are retained.

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

## Phase 4D documentary research expansion

The development corpus adds ten short factual paraphrases tied to official NASA pages: Mir, Apollo 1, Apollo 13, combustion background and three Spinoff accounts. They occupy a separate searchable documentary table, never the FLEX measurement table. Mir questions now retrieve historical evidence; unrelated incidents remain unsupported. ACME and FLEX-2 are catalogue-only pointers with no admitted numerical data. `migrations/phase4d.py` applies the reviewed manifest to a copy and preserves row hashes of the original scientific tables. `scripts/stage_research.py` prepares new official-source candidates in a local review queue only; it cannot admit them. See `research/PHASE4D_REPORT.md` for provenance, rights, tests and gaps.
