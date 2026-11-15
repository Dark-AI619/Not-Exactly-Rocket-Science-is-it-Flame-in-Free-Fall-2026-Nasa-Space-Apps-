# Phase 5 Pass A — connected research journey

## Scope

Pass A connects the existing workspaces through Streamlit session context. It does not add a simulation, change the database, use a Groq key, merge to `main`, or deploy.

The [official NASA Space Apps 2025 winners listing](https://www.spaceappschallenge.org/) names SpaceGenes+ (science), PureFlow (mission concept), and HerCode Space (storytelling). The project uses only broad principles implied by those categories: make scientific evidence approachable, give users a meaningful action, and tell a clear investigation story. No winner layout, asset, or branding was copied; their product interfaces were not assessed in this pass.

## Observed usability problems and changes

- The six pages previously lost the selected experiment. A lightweight session context now carries investigation, validated FLEX test, topic, and current question. Record-aware actions lead to measurements, comparison, source-grounded questions, Solution Lab, and View Effect.
- First use previously started in a dense catalogue. Research Explorer now offers one working verified example, FLEX–054, with a short path through the app.
- Research Records buried the result in a nine-row technical table. The reported outcome and three original values appear first; all cells, units, classifications, uncertainty markers, and provenance remain in expandable detail.
- Catalogue status codes now have readable display labels. The exact database codes remain available in source detail.
- A one-test comparison previously drew a box summary that suggested a distribution. That view now asks for at least three plotted tests; the original one-point scatter and source trace remain visible.
- View Effect previously showed generic FLEX PDF passages even when a test was selected. It now retrieves the selected experiment's actual admitted Table IX item. The flame image remains labeled conceptual; no mathematical simulation is present yet.

## Local browser journey

In a fresh local Streamlit session, clicked **Start with a verified FLEX experiment** in Explorer. Research Records opened FLEX–054 (Methanol, reported Extinction), showed the original 3.56 mm initial diameter, .41 mm²/s burning-rate constant, and 29 s burn duration, plus NASA/TP-2015-216046 Appendix A Table IX page 27. **Compare values** retained FLEX–054 and plotted its reported initial diameter against burn duration as one descriptive pair. **Ask about this test** prefilled a test-specific question and FLEX scope; evidence-only Assistant retrieved the experiment and its NASA citation. **Explore solutions** carried the question and investigation into Solution Lab. **View test context** retained FLEX–054 and displayed its Table IX item instead of unrelated pages. No page exception appeared.

The local service experienced one transient Windows socket failure during an edit/restart. A fresh listener and browser session completed the verification. No public deployment was accessed.

## Verification and remaining work

Targeted analysis, retrieval, and session tests passed; Python compilation and `git diff --check` passed. The existing scientific data and AI services were not changed. Pass B must implement and verify the mathematical simulation. Pass C must run the final full suite, responsive visual checks, and final judge journey before completion can be claimed.

**STOP after Pass A.**
