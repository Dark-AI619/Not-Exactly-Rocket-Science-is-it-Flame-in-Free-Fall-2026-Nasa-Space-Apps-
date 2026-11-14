# Flame in Freefall

An independent NASA Space Apps Challenge 2026 project by **Not Exactly Rocket Science, Is It?!**. This Phase 2 milestone is a Streamlit interface preview with six navigable research sections. Scientific database queries, charts, SQL execution, AI answers, and flame simulations are reserved for later integration. No sample measurements are invented.

## Run locally

Use Python 3.12. Install `requirements.txt`, then run `streamlit run app.py`. No API key is required.

## Research status

Phase 1 produced a separately preserved, validated transcription subset of FLEX Table IX from [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456). The interface deliberately does not query that database yet. BASS-II, SAME-R, and Saffire record-level data remain under validation. NASA PSI investigation pages are research sources, including [FLEX PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69). Original units, source pages, rights, and uncertainty must be carried forward when integration begins.

## Artwork and attribution

The project owner supplied two images. The astronaut and NASA International Space Apps Challenge artwork appears only in the Research Explorer hero, with its branding preserved. The flame-over-Earth artwork appears in View Effect as a conceptual illustration, not experimental footage. Their use does not imply that NASA operates or endorses this independent dashboard.

## AI assistance

ChatGPT/Codex assisted with Phase 1 data preparation and Phase 2 code and design. Generated Python files carry the required co-author comment. The application has no active AI features in this milestone.

## Phase 3A research audit

The research catalogue migration and audit are documented in `research/PHASE3A_REPORT.md`. The repository includes a compressed, topic-indexed copy of the validated Phase 1 database at `data/flame_research.db.gz`. The 3A checkpoint prepared source classifications without connecting the database to the Streamlit pages.

## Phase 3B backend

The standalone `backend` package provides read-only scientific data services, integrity validation, Pandas/NumPy descriptive summaries, FTS5 passage search, and a restricted SQL interface over approved projections. See `research/PHASE3B_REPORT.md` for its scope and limits. Run `python -m pytest tests/test_backend.py tests/test_phase3a.py -q` with `requirements.txt` and `requirements-dev.txt` installed. Streamlit integration begins only after the 3C checkpoint is approved.
