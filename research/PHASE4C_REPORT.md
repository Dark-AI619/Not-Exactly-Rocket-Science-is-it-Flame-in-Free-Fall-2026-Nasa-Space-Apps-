# Phase 4C — AI Research Assistant and Solution Lab

Checked 2026-11-15. This checkpoint connects the existing Assistant and Solution Lab Streamlit pages to the Phase 4B grounded-answer service. The other four pages and the scientific database were not changed. The public Streamlit deployment and `main` remain on the earlier Phase 3B commit.

## Interaction

Assistant retrieves an evidence packet for the selected investigation and topic, optionally requests an explanation, and displays only claims that passed the 4B checks. Citation markers resolve to original NASA source titles, locations, experiment IDs and links in the evidence inspector. The conversation retains at most six user/assistant exchanges. Up to two preceding user questions, each capped at 300 characters, may clarify phrasing; previous generated answers are not supplied as factual context. The current question's routed evidence alone supports generated claims. Users can select an investigation or topic scope for follow-up questions.

Solution Lab uses the same cached Groq adapter and `research_turn` function. It separates verified observations, scientific interpretation, conditional engineering directions, assumptions and limitations, and supporting citations. Its engineering text asks for condition matching and independent testing; it makes no certification claim. The model does not get a separate engineering pipeline or permission to create unverified measurements.

The owner configures the key privately. A missing key, missing factual evidence, rejected model output, rate limit, provider failure or session limit produces an explicit status and retains the deterministic packet. Both pages share one per-session request count, capped by `AI_SESSION_REQUEST_LIMIT` (default eight). Unsupported and no-key requests do not spend this budget. The interface never asks visitors to enter a key. A spinner covers retrieval and optional generation.

## Verification and limits

The full local suite passed **48 tests**. Added mocked tests cover bounded conversation history, exact FLEX Test 054 source citations and scope, provider rate-limit fallback, session budget exhaustion, missing-key and missing-evidence behavior. Python compilation and `git diff --check` passed. A local Streamlit server was launched with `GROQ_API_KEY` unset and inspected in Chrome. Assistant answered the Test 054 query in deterministic evidence mode and displayed the original report page in its inspector. Solution Lab displayed four FLEX evidence items and all requested sections for an extinction question. No Streamlit exception or layout overflow was observed in those two inspected views.

No real key or live Groq completion was tested. Generated-claim validation remains heuristic; every scientific claim still requires human source inspection. Follow-up wording can be ambiguous unless the user selects a research scope. The interface does not claim model output is verified scientific fact. Phase 4D requires separate approval.
