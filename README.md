# Flame in Freefall

An independent NASA Space Apps Challenge 2026 project by **Not Exactly Rocket Science, Is It?!**. The six-section Streamlit interface is being connected to verified research in staged Phase 3 checkpoints. Checkpoint 3C connects Research Explorer and Research Records, and 3D adds descriptive FLEX comparisons on the development branch. AI answers and flame simulations are reserved for later checkpoints. No sample measurements are invented.

## Run locally

Use Python 3.12. Install `requirements.txt`, then run `streamlit run app.py`. No API key is required.

## Research status

Phase 1 produced a separately preserved, validated transcription subset of FLEX Table IX from [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456). Checkpoint 3C reads that subset: 273 validated report-extracted tests and 2,457 original measurement cells. The catalogue includes 329 searchable PDF page passages and 23 sources. BASS-II, SAME-R, and Saffire have no admitted numerical experiment rows. NASA PSI investigation pages are research sources, including [FLEX PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69). Original units, source pages, rights, and uncertainty are retained.

## Artwork and attribution

The project owner supplied two images. The astronaut and NASA International Space Apps Challenge artwork appears only in the Research Explorer hero, with its branding preserved. The flame-over-Earth artwork appears in View Effect as a conceptual illustration, not experimental footage. Their use does not imply that NASA operates or endorses this independent dashboard.

## AI assistance

ChatGPT/Codex assisted with Phase 1 data preparation and Phase 2 and 3 code and design. Generated Python files carry the required co-author comment. The application has no active AI answers in this milestone.

## Phase 3A research audit

The research catalogue migration and audit are documented in `research/PHASE3A_REPORT.md`. The repository includes a compressed, topic-indexed copy of the validated Phase 1 database at `data/flame_research.db.gz`.

## Phase 3B backend

The standalone `backend` package provides read-only scientific data services, integrity validation, Pandas/NumPy descriptive summaries, FTS5 passage search, and a restricted SQL interface over approved projections. See `research/PHASE3B_REPORT.md` for its scope and limits. Run `python -m pytest tests/test_backend.py tests/test_phase3a.py -q` with `requirements.txt` and `requirements-dev.txt` installed.

## Phase 3C research pages

Research Explorer browses domains, investigations, topics, source records, and PDF passage hits. Research Records filters the admitted FLEX Table IX subset, displays original measured tokens and units, shows missing cells and source-page provenance, and permits bounded read-only queries with CSV export. See `research/PHASE3C_REPORT.md` for verification and limitations. These changes are committed to a development branch; Phase 3 does not publish new functionality to the public Streamlit demo.

## Phase 3D scientific comparisons

Compare & Analyze filters admitted FLEX tests by fuel, oxygen mole fraction, pressure and original test ID. It plots only pairs with both requested values, retains missing and source-classification status, shows original axis units, and includes a source-trace table. The scatter and fuel distribution are descriptive views of the selected subset; changing experimental conditions are flagged. See `research/PHASE3D_REPORT.md` for numerical checks and limits. Plotly is required in addition to the existing runtime packages.
