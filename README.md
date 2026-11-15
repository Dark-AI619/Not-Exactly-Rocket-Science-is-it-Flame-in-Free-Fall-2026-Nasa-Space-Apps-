<div align="center">

# 🔥🚀 FLAME IN FREEFALL

### What happens to fire when gravity lets go?

**Explore NASA experiments. Follow the evidence. Bring the mathematics to life.**

![NASA Space Apps astronaut artwork](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/raw/refs/heads/phase3-integration/assets/space_apps_astronaut.jpg)

**Built by Not Exactly Rocket Science, Is It?!**<br>
*An independent NASA Space Apps Challenge 2026 project*

[🚀 Explore the App](https://flame-in-freefall-2026.streamlit.app/) · [💻 Completed Application](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/tree/phase3-integration) · [🧭 Take the Judge Tour](#-your-three-minute-mission)

**273 verified FLEX tests · 329 searchable NASA report pages · 6 connected workspaces**

</div>

---

## 🌌 The problem: valuable science, difficult to explore

Understanding combustion in microgravity matters to spacecraft fire-safety research. Yet the evidence often lives inside long technical reports: dense tables, unfamiliar test identifiers, scattered source passages, and measurements with important limitations.

For students, curious explorers, and hackathon judges, finding a number is only the beginning. Understanding what was measured, where it came from, and what it can support takes more work.

**We built Flame in Freefall to make that journey accessible.**

## 💡 Our solution: turn a NASA report into an investigation you can follow

Start with a real experiment. Inspect its conditions. Compare its measurements. Ask a question with the evidence beside you. Then explore a mathematical droplet model using compatible source values.

The selected experiment travels with you through the app.

> **Discover → Investigate → Analyze → Ask → Explore Solutions → Simulate**

Our team brings verified report data, scientific visualization, evidence retrieval, and interactive mathematics into one connected research experience.

## 🛰️ What we built

| Workspace | The experience |
| --- | --- |
| 🔎 **Research Explorer** | Discover NASA investigations and scientific topics, or begin immediately with a selected verified FLEX experiment. |
| 📋 **Research Records** | Explore original reported values, units, missing measurements, and source pages. Filter experiments or use bounded read-only SQL. |
| 📊 **Compare & Analyze** | Investigate measurement relationships through interactive charts, with units, exclusions, and source traceability. |
| 🤖 **AI Research Assistant** | Ask research questions and inspect the supporting citations. Optional Groq generation adds explanations checked against retrieved evidence. |
| 🛠️ **Solution Lab** | Connect research observations to engineering questions and conditional design considerations. |
| 🔥 **View Effect** | Play, pause, and reset a D-squared droplet model. Load compatible NASA report parameters and watch the calculated diameter change. |

## 🧭 Your three-minute mission

**Begin with FLEX–054. Follow it all the way to the model.**

1. **Discover:** select **Start with a verified FLEX experiment** in Research Explorer.
2. **Investigate:** inspect the original measurement cells and NASA report citation.
3. **Analyze:** select **Compare values** to explore initial droplet diameter against reported burn duration.
4. **Ask:** select **Ask about this test**, submit the question, and open its evidence citation.
5. **Explore:** continue to **Explore solutions** to inspect supporting observations.
6. **Simulate:** select **Open droplet model**, load compatible D₀ and K values, and press **Play**.

**One experiment. A continuous path from source to understanding.**

## 🔥 Mathematics you can see

<div align="center">

![Conceptual flame suspended above Earth](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/raw/refs/heads/phase3-integration/assets/flame_over_earth.png)

*Fire-in-space artwork supplied by the project owner; conceptual illustration.*

### D(t)² = D₀² − Kt

</div>

Change the initial droplet diameter or burning-rate parameter. Follow the diameter-versus-time curve as the glowing schematic shrinks. Compare illustrative inputs with compatible parameters from a validated FLEX record.

| Model quantity | Unit |
| --- | --- |
| Initial liquid-droplet diameter, D₀ | mm |
| Constant burning-rate parameter, K | mm²/s |
| Model elapsed time, t | s |

The warm core and halo are a **schematic flame visualization**. The size follows the liquid-droplet model; the glow is illustrative and is **not an experimentally observed flame image**.

The constant-K model is a teaching approximation. It does not predict flame geometry, extinction, oxygen response, or spacecraft safety. NASA's reported D₀ and fitted K use different time references, so the app displays the reported burn duration separately from the calculated endpoint. **258 admitted tests** meet the source-input compatibility checks.

## 🧪 Real evidence at the center

| Research collection | Included |
| --- | ---: |
| Validated FLEX report-extracted tests | **273** |
| Original measurement cells, including missing-value markers | **2,457** |
| Searchable PDF page passages | **329** |
| Source-linked documentary notes | **10** |
| Catalogued sources | **25** |

Our numerical foundation is a validated subset of **NASA/TP-2015-216046, Appendix A, Table IX**. Original printed values, units, source pages, classifications, and missing values remain inspectable.

The dataset contains report-extracted records, not original PSI telemetry. BASS-II, SAME, and Saffire supply research context; numerical experiments from those families have not been admitted.

### Why the evidence matters

- **Trace every plotted point:** follow its test identifier and source page.
- **See missing data:** unavailable values remain visible and are excluded from incompatible chart pairs.
- **Inspect AI support:** citations and numerical-token checks accompany optional generated explanations.
- **Keep observations intact:** calculated model outputs never enter the verified research database.

The app works without an API key in evidence mode. Optional Groq generation requires private owner configuration; live authenticated generation remains to be verified. Automated claim checks are heuristic, so source inspection remains part of the experience.

## 🎯 Who this helps

**Students and educators** can move from an abstract combustion equation to an interactive example grounded in a NASA report.

**Research explorers** can inspect values, conditions, and citations without manually navigating hundreds of report pages.

**Engineering learners** can connect published observations to design questions while seeing the limits of the available evidence.

Our contribution is an accessible route through the science: every interpretation has a path back to its source.

## ⚙️ Built with

**Python · Streamlit · SQLite FTS5 · Pandas · NumPy · Plotly · optional Groq**

Read-only data services connect the verified corpus to the interface. Category-routed retrieval supplies bounded evidence packets. Python computes the droplet trajectory, while Plotly and the schematic show the same model state.

**Verification:** 70 automated tests passed in the final integration run. The visual refinement passed 17 targeted simulation tests, with local browser inspection of the connected judge journey, charts, and model playback.

## 🚀 Run it yourself

Use **Python 3.12** and the completed application branch:

```sh
git clone --branch phase3-integration https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-.git
cd Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-
python -m venv .venv
```

Activate your environment, then:

```sh
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

For Streamlit Community Cloud, select **branch `phase3-integration`** and entry point **`app.py`**. The public demo may show the earlier preview until the owner completes redeployment.

No key is required for evidence mode. Optional generation uses `GROQ_API_KEY` in private environment variables or Streamlit secrets. See [configuration options](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/blob/phase3-integration/.env.example). Per-session request limits do not cap aggregate public use.

## 📚 NASA sources

- [Detailed Results From the Flame Extinguishment Experiment (FLEX)](https://ntrs.nasa.gov/citations/20150023456)
- [NASA technical reference supporting the D-squared model](https://ntrs.nasa.gov/citations/19820015544)
- [NASA PSI — FLEX investigation](https://psi.nasa.gov/physci/repo/data/investigations/PSI-69)
- [Scientific model assumptions and verification](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/blob/phase3-integration/research/PHASE5B_REPORT.md)
- [Source admission architecture](https://github.com/Dark-AI619/Not-Exactly-Rocket-Science-is-it-Flame-in-Free-Fall-2026-Nasa-Space-Apps-/blob/phase3-integration/research/ADMISSION_ARCHITECTURE.md)

## 👩‍🚀 Meet the team

### Not Exactly Rocket Science, Is It?!

We built **Flame in Freefall** to make NASA combustion research easier to explore, question, and understand.

ChatGPT/Codex assisted with data preparation, implementation, and interface design. The project owner supplied the astronaut/Space Apps and flame-over-Earth artworks. Source and artwork rights remain subject to their respective terms; inclusion does not grant downstream reuse rights.

This is an independent NASA Space Apps Challenge project. NASA does not operate or endorse the application.

---

<div align="center">

### 🔥 Follow the experiment. Find the evidence. Watch the mathematics move.

**FLAME IN FREEFALL — by Not Exactly Rocket Science, Is It?! 🚀**

</div>
