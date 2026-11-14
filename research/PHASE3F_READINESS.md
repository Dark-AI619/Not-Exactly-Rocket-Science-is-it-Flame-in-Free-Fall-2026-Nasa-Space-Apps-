# Phase 3F — local integration readiness

Checked 2026-11-15. This is a verification checkpoint for the six-section Streamlit app and the validated SQLite snapshot. It does not publish Phase 3 to Streamlit Community Cloud.

## Scope and integrity

`validate_database` returned `VALIDATED_SUBSET`: **273** FLEX experiments, **2,457** original measurement cells, **329** searchable PDF page passages and **23** catalogued sources. All admitted experiment rows retain `NASA_REPORT_EXTRACTED`; original PSI telemetry is not claimed. There are **108** unavailable measurement cells, **zero** original tokens with a `~` or `≈` prefix, and **zero** cell-level uncertainty entries in this subset. The UI preserves missing cells and labels uncertainty as unreported. BASS-II has 20 admitted documentary passages and no numerical rows; Saffire, SAME-R and SPICE have no admitted numerical experiment rows.

## Verification matrix

| Area | Result |
| --- | --- |
| SQLite integrity, foreign keys, FTS5 count, topic/source links, units, physical ranges, rights | Passed by `validate_database` and tests |
| Research categories, investigation aliases, synonyms, topic filters and narrow scope | Passed by retrieval tests |
| FLEX records, filters, original values, page provenance, CSV and read-only SQL | Passed by backend tests and local browser inspection |
| SQL modifications, hidden tables and unsafe functions | Rejected by existing security tests; authoritative archive unchanged |
| FLEX charts, original units, missing pairs and source trace | Passed by analysis tests and local browser inspection; default 260 complete diameter/duration pairs |
| Assistant, Solution Lab and View Effect | Local browser showed cited retrieval, separate engineering questions, verified test context and conceptual-artwork labeling |
| Six-page navigation and desktop overflow | All six pages opened locally without a Streamlit exception; 1280 px browser width showed no horizontal page overflow in checked views |
| API credentials and fabricated rows | No mandatory API key references found in app/backend/requirements; database counts and displayed records stayed within the validated subset |

`python -m pytest tests -q` passed **30 tests** with no failures. `python -m py_compile app.py backend/retrieval.py backend/analysis.py backend/store.py` and `git diff --check` passed. A local Python 3.12 session loaded and audited the SQLite archive in **25.2 ms** and ran the five representative retrieval questions in **14.6 ms total** after loading. These are single-machine measurements, not production latency guarantees.

## Five representative questions

1. **Flame extinction in FLEX:** FLEX-only PDF passages and a verified PSI objective summary, with source titles and PDF pages. Supported as documentary evidence.
2. **Measurements for FLEX Test 054:** One validated Table IX test, nine original measurement tokens and units, PDF page 27 and NASA report link. Supported for this test.
3. **Mir station fire:** A verified official NASA catalogue pointer is returned, with a clear notice that no approved passage supports a factual account. **Acceptance gap:** the requested historical account is not yet answerable from the admitted corpus.
4. **BASS-II versus FLEX burning rates:** Separate FLEX and BASS-II documentary citations. A notice identifies FLEX's liquid-droplet burning-rate constant in mm²/s, BASS-II's solid-material scope and the absence of BASS-II structured rate rows. No numerical comparison is made.
5. **Oxygen concentration and FLEX outcomes:** Three validated Table IX example tests at original O₂ mole fractions 0.12, 0.20 and 0.34, each with original measurements and report pages, plus relevant PDF passages. The interface warns that these examples have different conditions and cannot establish causation.

The retrieval service returns at most 15 evidence items per packet. Cross-investigation questions retain investigation labels; explicit BASS-II scope does not pull FLEX passages. Catalogue-only pointers do not count as factual evidence.

## Readiness decision and remaining work

**Ready for the supported FLEX report-extracted scope and documentary research inspection.** It is not ready to answer every historical or cross-investigation question. The Mir factual-answer gap requires review and admission of an official passage under the controlled source process. BASS-II numerical comparison requires separately validated experiment measurements. Authentic experiment media and any generative answer mode need verified rights, provenance and evaluation before activation. Phase 3 remains on `phase3-integration`; production publishing belongs to a later user-directed step.

No scientific dataset or frontend artwork was changed in this checkpoint. The code change adds bounded source-backed examples for the oxygen/outcome question and a precise FLEX/BASS-II compatibility notice. `tests/test_phase3f.py` locks the five-question behavior to the admitted corpus.
