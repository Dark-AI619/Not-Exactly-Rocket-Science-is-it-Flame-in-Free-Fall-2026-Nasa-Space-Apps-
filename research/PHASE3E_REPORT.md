# Phase 3E — deterministic, evidence-grounded retrieval

Checked 2026-11-15. This checkpoint builds a retrieval service independently of any LLM and connects it to Assistant, Solution Lab and View Effect on the development branch. The public Streamlit app remains at the earlier milestone.

## Implementation

- `backend/retrieval.py` routes a question through intent, research domain, investigation aliases and scientific topic synonyms. It uses the SQLite FTS5 index with investigation/topic metadata filters and bounded per-investigation candidate sets. It tries narrow topic matches first, logs related-topic or investigation-level expansion, and keeps cross-investigation evidence in separately labeled scopes.
- Exact FLEX test questions retrieve the validated report record and all nine original measurement tokens with units, classification, uncertainty field and PDF page. They do not import unrelated PDF hits. Missing test IDs return a clear absence notice.
- Citations carry source title, source identifier, investigation, page or section, optional test ID, verification status and NASA URL. Catalogue-only pointers are labeled as pointers and do not become factual answers.
- `app.py` provides deterministic evidence summaries in the Assistant, optional investigation/topic scopes, a source inspector, problem-based retrieval in Solution Lab, and verified test conditions beside the conceptual View Effect artwork. Streamlit caches bounded evidence packets; the pure router has a small LRU cache. No external API key is required.
- `OptionalLLMProvider` is an interface for a future reviewed integration. It is not instantiated or evaluated. `research/ADMISSION_ARCHITECTURE.md` describes the future controlled admission path without enabling public writes.

## Verification

`python -m pytest tests/test_retrieval.py tests/test_analysis.py tests/test_backend.py tests/test_phase3a.py -q` passed **29 tests** after the final changes. The tests cover aliases, topic routing, bounded citations, exact FLEX Test 054, missing Test 999, Mir's catalogue-only status, BASS-II/FLEX separation and explicit investigation scope. Five representative retrieval requests completed in approximately **7.1 ms total** in one loaded local SQLite session, returning at most six items each; this is a local benchmark, not a production latency guarantee.

A local browser session showed Assistant returning a cited FLEX Test 054 experiment and its nine-cell table, Solution Lab retrieving oxygen/extinction passages while separating engineering questions, and View Effect displaying the supplied flame artwork with verified FLEX Test 001 conditions and links. After the relevance correction and restart, the Assistant's exact-test query showed two focused items—the validated test and the FLEX objective—with no unrelated PDF hits. The correction is covered by tests.

## Limits

The existing corpus has 309 FLEX and 20 BASS-II PDF page passages, approved PSI objective summaries, and catalogue pointers for other areas. Mir's official source is catalogued but has no admitted passage, so the service cannot answer what happened from the approved corpus. BASS-II has no admitted numerical experiment rows and cannot be compared numerically with FLEX burning-rate values. Retrieved excerpts are evidence for inspection, not generated synthesis or causal conclusions. No authentic experimental footage is admitted for View Effect. No generative RAG claim is made.

**Checkpoint: 3E complete on the development branch. Await explicit approval before 3F.**
