# Phase 3A — database audit and research organization

Checked 2026-11-14. This checkpoint adds research metadata and a source catalogue. The six-page Streamlit frontend remains at the Phase 2 visual milestone.

## Verified starting state

| Item | Count | Evidence |
|---|---:|---|
| Admitted FLEX experiments | 273 | All `NASA_REPORT_EXTRACTED`, `VALIDATED`; original test IDs preserved |
| Measurement cells | 2,457 | Nine fields per admitted test; original tokens and units retained |
| Explicit unavailable cells | 108 | Null numeric values; no imputation |
| Searchable PDF page passages | 329 | 309 FLEX report pages, 20 BASS-II report pages |
| Supplied PDF source records | 7 | All seven local PDF hashes match the source manifest |

The FLEX source is [NASA/TP-2015-216046](https://ntrs.nasa.gov/citations/20150023456), Table IX on PDF pages 26–34 (printed pages 20–28). The report describes 284 tests; that is **not** the admitted experiment count. The extraction produced 274 structured rows, of which 273 passed Phase 1 validation. FLEX–114 is held for the source's zero-pressure anomaly. FLEX–227 and FLEX–229 were not admitted after damaged text extraction. See the preserved Phase 1 data-quality report for the complete exception list.

Existing tables are `investigations`, `sources`, `experiments`, `measurements`, `passages`, and `passages_fts`, with primary and unique keys, foreign keys, and an insert trigger for FTS5. The original four core tables `sources`, `experiments`, `measurements`, and `passages` have identical row-content hashes before and after migration. `investigations` gains one metadata-only SPICE row.

## Phase 3A additions

- Six research domains and 17 named scientific topics.
- 23 source-catalogue entries: seven supplied PDFs and 16 official-resource URLs. Each has identity, publisher, domain, topic, investigation where applicable, verification, rights, and admission status.
- 329 of 329 passages have at least one topic link. There are 1,166 passage-topic links total. Keyword-derived links are marked `KEYWORD_IN_TEXT` and should be treated as candidate retrieval tags, not manually verified claims.
- All 2,457 measurements have a topic link based on their original variable name. All 273 FLEX experiments have topic links.
- Five short paraphrases of investigation objectives from PSI pages with explicit CC0-1.0 metadata. These are `PARAPHRASED_OBJECTIVE` documentary evidence, **not** raw experiment rows or PDF passages.
- An `investigation_coverage` table separates numerical and documentary coverage.

| Investigation | Admitted experiments | Admitted PDF passages | Gap |
|---|---:|---:|---|
| FLEX | 273 | 309 | Original PSI telemetry not acquired |
| BASS-II | 0 | 20 | Numerical records not admitted |
| Saffire | 0 | 0 | Report and PSI references only |
| SAME-R / SAME | 0 | 0 | Report and PSI references only |
| SPICE | 0 | 0 | Investigation metadata and objective summary only |

The PSI investigation metadata independently identifies [FLEX / PSI-69](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69), [BASS-II / PSI-25](https://psi.nasa.gov/physci/repo/data/investigations/PSI-25), [Saffire-I / PSI-98](https://psi.nasa.gov/physci/repo/data/investigations/PSI-98), [SAME-R / PSI-101](https://psi.nasa.gov/physci/repo/data/investigations/PSI-101), and [SPICE / PSI-107](https://psi.nasa.gov/physci/repo/data/investigations/PSI-107). Their repository metadata states CC0-1.0. PSI-99 and PSI-100 are catalogue-only because their individual page content was not independently readable during this audit. The [NASA Science Data license guidance](https://science.data.nasa.gov/about/license) says to honor each dataset's own license and verify third-party rights.

NASA [combustion background](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/), the [researcher's guide](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/), [Apollo 1](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1), the [Mir fire history](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/), and three NASA Spinoff pages are catalogue-only pending reuse review. Apollo 13 and the ScienceCasts video are listed but not independently verified in this checkpoint. Historical incidents and technology-transfer examples are kept outside the experimental measurement domain. Apollo 13 is not a controlled combustion experiment.

## Migration and checks

`migrations/phase3a.py` copies the Phase 1 database, preserves a byte-identical local pre-migration backup, applies additive schema changes, and writes a deterministic gzip archive for the repository. It refuses to overwrite an existing output or backup. The original Phase 1 database and PDFs were not modified.

Checks passed: SQLite `integrity_check`, `foreign_key_check`, seven PDF SHA-256 checks, the Phase 1 FLEX validation script, original core-table row-hash comparison, FTS5 count, topic-link coverage, missing-value preservation, and three Phase 3A unit tests. The portable database archive is `data/flame_research.db.gz`; the uncompressed local database and its backup remain outside Git tracking.

## Scientific limits and next checkpoint

The measured subset supports descriptive FLEX analysis only. Burning-rate constants are report-derived; Table IX provides no row-level uncertainty. Text-layer passages support page discovery and require visual source checks before numerical claims. No BASS-II, Saffire, SAME-R, or SPICE numerical rows were created. No frontend or backend service integration has begun.

**Checkpoint: 3A complete. Await explicit approval before 3B.**