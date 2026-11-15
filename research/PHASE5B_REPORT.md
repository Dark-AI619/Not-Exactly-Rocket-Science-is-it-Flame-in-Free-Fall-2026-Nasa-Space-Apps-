# Phase 5 Pass B — bounded droplet model

## Scientific basis

NASA's technical treatment of the D-squared law integrates constant square-diameter regression to **D(t)² = D₀² − Kt** and gives the ideal zero-diameter time **D₀²/K**. It also describes early heating transients and other departures from the classical assumptions. [NASA technical reference, section 3](https://ntrs.nasa.gov/api/citations/19820015544/downloads/19820015544.pdf).

NASA/TP-2015-216046 Appendix A defines FLEX Table IX `Actual D0` at the moment the igniters turn on and `Burning rate` as an average linear fit from shortly after ignition to extinction. Those intervals do not share a directly observed zero point. The user interface therefore labels a source-loaded curve a **teaching approximation**, not a reconstruction or prediction of reported burn duration, extinction, flame shape, oxygen response, or spacecraft safety. [FLEX report, Appendix A](https://ntrs.nasa.gov/api/citations/20150023456/downloads/20150023456.pdf).

## Implementation

- `backend/simulation.py` computes the diameter and ideal endpoint in Python using mm, mm²/s, and s. Inputs and elapsed time must be finite and physically positive; the model never takes the square root of a negative value. The profile is bounded to 121 points by default.
- View Effect preserves the supplied flame-over-Earth artwork as conceptual art. A separate cyan circle represents *liquid droplet diameter only* and updates with the Plotly diameter-versus-model-time curve. Play, pause, reset, current model time, predicted diameter and ideal endpoint all use the same model state.
- The default sliders are explicitly illustrative. A visitor may load D₀ and K only from a validated FLEX report-extracted record with exact original mm and mm²/s units, positive numeric values, acceptable printed tokens, and preserved source-page provenance. 258 of the 273 admitted FLEX tests satisfy this gate. Missing, approximate, or incompatible cells keep illustrative mode and explain why.
- The original FLEX outcome and burn-duration token appear separately as report observations. The model never writes to SQLite. Selecting a different test clears a previously loaded test's parameter identity.
- Existing research retrieval, restricted SQL, Groq integration, and source records were not changed. The archive SHA-256 remains `eac5e312c366a0684131d44447c4b9c75bbdd3f9af1e647fbd9a74b5ba67cd3f`.

## Verification

- `tests/test_simulation.py`: 17 focused tests passed for the equation, units, endpoint, monotonic profile, invalid inputs, missing data, unit mismatch, approximate token rejection, and FLEX–054 source trace. The targeted simulation, analysis, retrieval, and session set passed 29 tests.
- Python compilation and `git diff --check` passed.
- In a local browser, View Effect rendered the illustrative 3.00 mm / 0.40 mm²/s model with a 22.5 s ideal endpoint. Play advanced model time and changed the predicted circle and chart marker; Pause stopped playback; Reset restored 0.0 s and 3.00 mm. A slider change recalculated the diameter and endpoint.
- Loading FLEX–054 showed D₀ 3.56 mm (MEASURED) and K .41 mm²/s (DERIVED), both on PDF page 27, with a separate reported 29 s burn duration and Extinction outcome. The model endpoint displayed 30.9 s and was labeled mathematical, not observed. Selecting FLEX–009, whose burning-rate cell is unavailable, withheld source loading and reset to illustrative values.
- One PTY-hosted local Streamlit listener dropped its Windows socket while testing. Relaunching as a hidden local process with logs allowed the controls to be verified. This was a local test-environment issue, not a claim about hosted behavior.

## Remaining limitations

The D-squared model assumes a constant K and does not capture transient heating, chemistry, convection, radiative extinction, droplet disruption, or actual flame geometry. The schematic playback uses model-frame steps rather than wall-clock experimental timing. Approximate original tokens are excluded from automatic source loading. Phase C still needs full-suite testing, responsive review, the final judge journey, and release verification. No deployment or live Groq call occurred.

**STOP after Pass B.**
