# Phase 4D — documentary research coverage and controlled admission

Checked 2026-11-15. The development corpus now contains **10 short, source-linked factual paraphrases** in a separate `documentary_evidence` table with FTS5 search. They are historical/background/technology evidence, not numerical experiment measurements or copied article text. Mir has two admitted notes, so a Mir question can return a factual historical packet for the first time. The original **273** FLEX experiments, **2,457** measurement cells and **329** PDF page passages are unchanged.

## Source comparison and categories

| Category | Official source | Admitted notes | Source location |
| --- | --- | ---: | --- |
| Historical incident | [Mir fire history](https://www.nasa.gov/history/25-years-ago-fire-aboard-space-station-mir/) | 2 | Article introduction; Kvant-1 incident; crew response |
| Historical incident | [Apollo 1 AS-204](https://sma.nasa.gov/sma-disciplines/accllp/apollo-1) | 2 | Accident; investigation; lessons learned |
| Historical system accident | [Apollo 13](https://sma.nasa.gov/sma-disciplines/accllp/apollo-13) | 1 | Oxygen tank explosion; not a flame experiment |
| Scientific background | [Combustion Science](https://www.nasa.gov/glenn/glenn-expertise-space-exploration/physical-sciences-program/combustion-science/) | 1 | Archived investigations and Combustion Integrated Rack |
| Scientific background | [ISS combustion guide](https://www.nasa.gov/missions/station/a-researchers-guide-to-combustion-science/) | 1 | Article overview |
| Technology transfer | [Fire Detector](https://spinoff.nasa.gov/node/9407), [Fireman's Air Tanks](https://spinoff.nasa.gov/node/9582), [Fire Attire](https://spinoff.nasa.gov/node/9918) | 3 | Each article summary |

Each paraphrase was manually compared with the named official page and its section. `source_catalogue` records publisher, stable URL, verification, rights basis, category and admission state; `documentary_evidence` records source key, section, topic, summary digest, review method and check date. The [NASA web media guidance](https://www.nasa.gov/nasa-brand-center/images-and-media/) was checked for use restrictions. The admitted content is factual paraphrase only; no NASA photographs, logos, video, long passages or third-party material were copied. This is recorded as `NASA_WEB_FACT_PARAPHRASE_ONLY`, **not** as a claim that entire pages are CC0. [NASA Science Data license guidance](https://science.data.nasa.gov/about/license) applies separately to datasets and does not automatically license every website element. Source links remain visible for independent inspection. The source pages were not snapshotted locally, so later content changes would require rechecking.

[FLEX-2](https://gipoc.grc.nasa.gov/wp/fcf-cir/flex-2/) and [ACME](https://science.nasa.gov/biological-physical/investigations/acme/) were inspected and added as catalogue-only official pointers. Existing BASS-II, Saffire, SAME-R and SPICE sources and supplied reports were reviewed for coverage. No additional source in this checkpoint supplied a fully validated test-by-test table with original values, units, metadata and rights sufficient for numerical admission. Their numerical coverage remains zero. No authentic footage was admitted. NASA PSI archives were not repeatedly retried; the earlier access gap remains documented.

## Admission mechanics and verification

`research/phase4d_admissions.json` is the reviewable manifest. `migrations/phase4d.py` writes a new gzip archive from a copy, checks source URLs and topic/domain alignment, rejects duplicate locations or changed manifest versions, and records `corpus_versions` and `admission_audit`. The migration was rerun on its own output: both runs produced the same SHA-256 archive digest, `eac5e312c366a0684131d44447c4b9c75bbdd3f9af1e647fbd9a74b5ba67cd3f`. Row hashes for `sources`, `experiments`, `measurements` and `passages` matched before and after migration. SQLite integrity and foreign keys pass; documentary FTS contains ten searchable rows. The source catalogue now has 25 entries. A separate `scripts/stage_research.py` writes candidate metadata to a local, non-production review queue; it never changes the approved corpus. Duplicate, rejected and catalogue-only candidates remain excluded.

The routing tests verify Mir evidence is available and isolated from FLEX, Apollo 1 and technology-transfer records. An unrelated Cosmos station-fire question remains unsupported. The model's mocked Mir claim cites only a supplied Mir evidence ID. Existing scientific tests still guard the FLEX subset and BASS-II/FLEX incompatibility. No live Groq call or public Streamlit deployment occurred in this checkpoint.

The complete local suite passed **53 tests**. Python compilation and `git diff --check` passed. With `GROQ_API_KEY` unset, a local Streamlit session was inspected in Chrome: Explorer displayed the new corpus counts, a Mir search returned its two documentary notes and source link, and Assistant returned those two Mir notes in deterministic evidence mode without a Streamlit exception. The staging CLI was exercised against a temporary candidate; its test queue was removed afterward.

## Remaining gaps

BASS-II, Saffire, SAME-R, SPICE, FLEX-2 and ACME still have no admitted structured numerical tests beyond the FLEX Table IX subset. The historical notes are short factual summaries and do not replace primary incident investigations. The local review queue has no production identity, durable source snapshots or automatic approval, and must not be described as autonomous ingestion. The public deployment and `main` remain unchanged until a later owner-directed release.
