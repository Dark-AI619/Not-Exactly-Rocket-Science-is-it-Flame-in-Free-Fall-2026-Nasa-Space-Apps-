# Phase 4B — grounded generative answer service

Checked 2026-11-15. This checkpoint adds an optional, fail-closed generative service around the Phase 3 evidence router. The Streamlit interface, scientific database, public deployment and `main` were not changed.

## Evidence path

`answer_question` calls `retrieve_evidence` with the existing domain, investigation, topic and exact-test routing. Only admitted passages, objective summaries and validated FLEX report-extracted experiment records enter a model request; catalogue pointers are excluded. Mir incident questions with no admitted factual passage return `missing_evidence` without a model call. Cross-investigation packets preserve each item's investigation and source metadata; no BASS-II numerical measurements are invented. Up to six items are admitted to the prompt, stopping before its JSON context exceeds 11,000 characters. The model receives no database connection, full PDF library, secrets or conversation history.

The model is asked for one to four short JSON claims with supplied evidence IDs. Each claim must cite an ID actually present in that request. Numeric tokens must occur in the cited item's experiment identifier, excerpt or original measurement values and uncertainty; report identifiers and PDF page numbers alone cannot justify a measurement claim. A lexical relevance check rejects claims with insufficient overlap to the cited evidence, plus explicit overclaim and prompt-injection patterns. The output retains the original evidence packet and renders validated citation markers. Raw generated text is removed from the returned model metadata, including rejected outputs. Missing keys, provider failure, invalid JSON, unsupported claims and unsafe evidence yield deterministic evidence-only results.

These checks are deliberately conservative and **cannot prove semantic truth or eliminate hallucinations**. In particular, a number appearing in a cited passage is not proof that every relation involving that number is correct. The source-linked evidence packet remains available for human inspection. This service does not calculate derived values or interpret measurements beyond the admitted text.

## Verification

Offline mocked tests cover exact FLEX Test 054 routing, unrelated-category exclusion, BASS-II/FLEX separation, Mir missing evidence, no-key behavior, fabricated citation IDs, unsupported numerical claims, report-number misuse, invented fuel wording, prompt injection in source and response, provider timeout, rate limits, authentication failure, deterministic fallback and prompt size limits. No real Groq key was used and no live model call was made. Phase 4C will connect this tested service to the Assistant and Solution Lab interfaces after approval.
