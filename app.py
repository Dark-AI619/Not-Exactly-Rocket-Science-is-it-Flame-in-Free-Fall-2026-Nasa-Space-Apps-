# Co-authored with ChatGPT
"""Flame in Freefall — source-linked research interface."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from backend import (DropletModel, GroqAdapter, QueryRejected, ResearchError, ResearchStore, RestrictedSQL,
                     build_comparison, compatible_report_inputs, load_groq_settings, research_turn, retrieve_evidence,
                     validate_database)

ASSETS = Path(__file__).parent / "assets"
ASTRONAUT = ASSETS / "space_apps_astronaut.jpg"
FLAME = ASSETS / "flame_over_earth.png"
MEASURE_LABELS = {
    "pressure_mmhg": "Atmospheric pressure · mmHg",
    "oxygen_mole_fraction": "Oxygen mole fraction",
    "nitrogen_mole_fraction": "Nitrogen mole fraction",
    "carbon_dioxide_mole_fraction": "Carbon dioxide mole fraction",
    "helium_mole_fraction": "Helium mole fraction",
    "initial_diameter_mm": "Initial droplet diameter · mm",
    "visible_extinction_diameter_mm": "Visible extinction diameter · mm",
    "burning_rate_mm2_s": "Burning-rate constant · mm²/s",
    "burn_time_s": "Burn duration · s",
}
SOURCE_LABELS = {
    "VERIFIED": "Report checked", "VERIFIED_PAGE": "NASA page checked",
    "PENDING_VALIDATION": "Awaiting review", "RIGHTS_UNCONFIRMED": "Rights review needed",
    "URL_LISTED": "Link listed", "PASSAGES_ADMITTED": "Searchable report text",
    "DOCUMENTARY_ADMITTED": "Source-linked summary", "CATALOGUE_ONLY": "Reference only",
    "PDF": "Report", "INCIDENT": "Historical event", "BACKGROUND": "Background",
    "INVESTIGATION": "Investigation", "VIDEO": "Video link",
}

st.set_page_config(page_title="Flame in Freefall", page_icon="🔥", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
:root {color-scheme:dark}
html, body, [class*="css"] {font-family:'DM Sans',sans-serif}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;letter-spacing:-.035em}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse at 85% -10%,#193039 0,transparent 36%),#10171b;color:#e9f2f4}
[data-testid="stSidebar"] {background:#0c1318;border-right:1px solid #2d3c43}
.block-container {max-width:1360px;padding:2.5rem 2.6rem 5rem}
[data-testid="stSidebar"] .block-container {padding-top:1.5rem}
[data-testid="stSidebarNav"] {padding-top:1.2rem}
[data-testid="stSidebarNav"] a {border-radius:9px;margin:.1rem .35rem}
[data-testid="stSidebarNav"] a:hover {background:#1b2d33}
[data-testid="stSidebarNav"] a[aria-current="page"] {background:#173138;color:#a9eef0}
.sidebrand {padding:.25rem .15rem 1rem;border-bottom:1px solid #2b3a40}
.sidebrand .mark {color:#ffa76c;font-size:1.45rem;line-height:1}
.sidebrand strong {font:700 1rem 'Space Grotesk',sans-serif;letter-spacing:.04em}
.sidebrand small {display:block;color:#97adb4;margin-top:.45rem;line-height:1.45}
.eyebrow {font-size:.72rem;letter-spacing:.19em;text-transform:uppercase;color:#82dce3;font-weight:700;margin-bottom:.7rem}
.lede {color:#b5c7cc;line-height:1.65;font-size:1.05rem;max-width:760px;margin:.2rem 0 1.45rem}
.section-title {font:600 1.35rem 'Space Grotesk',sans-serif;color:#f3f7f8;margin:1.5rem 0 .6rem}
.muted {color:#9fb4bb;font-size:.88rem;line-height:1.55}
.smallcaps {color:#83dbe1;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;font-weight:700}
.surface {background:#172329;border:1px solid #32454b;border-radius:14px;padding:1.25rem 1.35rem;margin:.3rem 0 1rem}
.surface h3 {font-size:1.06rem;color:#ecf5f5;margin:.2rem 0 .45rem}
.surface p {color:#b7c7cb;line-height:1.55;margin:0}
.surface.orange {border-top:2px solid #e9955e}
.surface.cyan {border-top:2px solid #62cbd3}
.surface .index {font-size:.75rem;color:#ec9d69;font-weight:700;letter-spacing:.12em}
.hero-copy {padding:1.3rem 0}
.hero-copy h1 {font-size:clamp(2.8rem,5vw,5rem);line-height:1.02;margin:.2rem 0 1.2rem}
.hero-art {background:#0b1217;border:1px solid #3b4d52;border-radius:18px;padding:8px}
.hero-art img, .effect-art img {width:100%;height:auto;object-fit:contain;display:block;border-radius:11px}
.hero-art figcaption {color:#a3b5bb;font-size:.73rem;padding:.65rem .45rem .25rem}
.statusline {border-top:1px solid #34474d;border-bottom:1px solid #34474d;padding:.8rem 0;color:#b9c9cd;font-size:.82rem;margin:1.2rem 0 2rem}
.statusline b {color:#9ae4e8}
.table-wrap {background:#152127;border:1px solid #35505a;border-radius:13px;overflow-x:auto;margin:.55rem 0 1.2rem}
.data-table {width:100%;min-width:760px;border-collapse:collapse;font-size:.82rem}
.data-table th {background:#21333b;color:#9de2e6;text-align:left;padding:.9rem .85rem;white-space:nowrap;border-bottom:1px solid #45606a;font-weight:700}
.data-table td {padding:2.6rem 1rem;text-align:center;color:#aebec4}
.inspector-line {display:flex;justify-content:space-between;gap:.75rem;padding:.65rem 0;border-bottom:1px solid #30434a;font-size:.82rem}
.inspector-line span:first-child {color:#98b4bb}.inspector-line span:last-child {color:#e0edee;text-align:right}
.editor-head {display:flex;justify-content:space-between;align-items:center;margin:1.35rem 0 .55rem}
.code-frame {background:#0d171d;border:1px solid #35505a;border-radius:12px;padding:1.1rem 1.25rem;color:#9bdce1;font: .9rem Consolas,monospace;min-height:95px}
.chart-frame {background:linear-gradient(#20303765 1px,transparent 1px),linear-gradient(90deg,#20303765 1px,transparent 1px),#142127;background-size:52px 52px;border:1px solid #39535d;border-radius:13px;height:350px;position:relative;margin:.4rem 0 1rem}
.chart-empty {position:absolute;top:45%;left:50%;transform:translate(-50%,-50%);text-align:center;background:#142127e8;padding:1rem 1.4rem;border:1px solid #3b525b;border-radius:9px;color:#afc3c8;min-width:230px}
.chart-empty strong {display:block;color:#e7f1f1;margin-bottom:.4rem}
.axis-x {position:absolute;bottom:13px;left:50%;transform:translateX(-50%);color:#91b6be;font-size:.76rem}
.axis-y {position:absolute;left:12px;top:50%;writing-mode:vertical-rl;transform:translateY(-50%) rotate(180deg);color:#91b6be;font-size:.76rem}
.chat-window {background:#131f25;border:1px solid #37505a;border-radius:14px;min-height:360px;padding:1.1rem}
.chat-msg {max-width:84%;background:#21343c;border-left:2px solid #7bd9df;border-radius:4px 12px 12px 12px;padding:1rem 1.1rem;color:#d9e8eb;line-height:1.55}
.chat-msg small {display:block;color:#8cdae1;font-size:.7rem;letter-spacing:.1em;margin-bottom:.45rem}
.composer {border:1px solid #3b535c;border-radius:12px;color:#90a8af;padding:1rem;margin-top:1rem;background:#18282f}
.composer span {float:right;color:#78cbd2}
.effect-stage {background:radial-gradient(circle at 50% 45%,#1d353c,#0b1319 65%);border:1px solid #3c535b;border-radius:18px;padding:1.2rem;max-width:780px;margin:0 auto 1.4rem}
.effect-art {max-width:600px;margin:auto}
.effect-art img {border-radius:11px}
.effect-label {color:#adc2c7;font-size:.8rem;text-align:center;padding:.9rem .4rem .1rem}
.droplet-stage {height:220px;display:grid;place-items:center;background:radial-gradient(circle,#193d45,#101b20 70%);border:1px solid #3a5960;border-radius:14px;margin:.5rem 0 1rem}
.droplet {border-radius:50%;background:radial-gradient(circle at 32% 28%,#c1fcfa,#59cbd5 55%,#257987);box-shadow:0 0 18px #4bc6d444;border:1px solid #c2f8f6;transition:width .16s linear,height .16s linear}
.model-note {color:#a9c1c7;font-size:.84rem;line-height:1.55}
.step {display:inline-block;color:#f1a16d;font-size:.8rem;font-weight:700;margin-bottom:.5rem}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {background:#14232a;border:1px solid #3c555e;color:#e8f2f3}
div[data-testid="stSelectbox"] > div {background:#14232a}
div[data-testid="stTextInput"] label,div[data-testid="stSelectbox"] label,div[data-testid="stTextArea"] label {color:#c3d4d7}
div[data-testid="stAlert"] {border-radius:10px}
@media(max-width:800px){.block-container{padding:1.1rem 1rem 3rem}.hero-copy h1{font-size:2.8rem}.chart-frame{height:280px}.data-table{min-width:720px}}
</style>
""",
    unsafe_allow_html=True,
)


def html(markup):
    st.markdown(markup, unsafe_allow_html=True)


def heading(kicker, title, intro):
    html(f'<div class="eyebrow">{kicker}</div>')
    st.title(title)
    html(f'<p class="lede">{intro}</p>')


def surface(label, title, body, accent="cyan"):
    html(f'<div class="surface {accent}"><span class="smallcaps">{label}</span><h3>{title}</h3><p>{body}</p></div>')


def follow_experiment(experiment_id, *, destination):
    """Carry a validated record selection to a specific workspace."""
    st.session_state["active_investigation"] = "FLEX"
    st.session_state["active_experiment"] = experiment_id
    topic = st.session_state.get("active_topic")
    if topic:
        with ResearchStore() as store:
            if not any(row["id"] == topic and row["domain_id"] == "combustion" for row in store.topics()):
                st.session_state.pop("active_topic", None)
    if destination == "records":
        st.session_state["record_target"] = experiment_id
        st.switch_page(pages[1])
    if destination == "compare":
        st.session_state["compare_target"] = experiment_id
        st.switch_page(pages[2])
    if destination == "assistant":
        number = experiment_id[-3:]
        st.session_state["active_question"] = f"What measurements and outcome did FLEX test {number} report?"
        st.session_state["assistant_target"] = True
        st.switch_page(pages[4])
    if destination == "lab":
        st.session_state["lab_problem"] = st.session_state.get(
            "active_question", f"What evidence informs a design question about FLEX test {experiment_id[-3:]}?"
        )
        st.session_state["lab_investigation"] = "FLEX"
        st.switch_page(pages[3])
    if destination == "effect":
        st.session_state["effect_target"] = experiment_id
        st.switch_page(pages[5])


def journey_context(store, workspace):
    """Small record-aware handoff; stale session IDs are never shown as evidence."""
    experiment_id = st.session_state.get("active_experiment")
    if not experiment_id:
        return
    try:
        record = store.experiment(experiment_id)
    except ResearchError:
        st.session_state.pop("active_experiment", None)
        return
    if record["validation_status"] != "VALIDATED" or record["investigation_id"] != "FLEX":
        st.session_state.pop("active_experiment", None)
        return
    st.caption(f'FOLLOWING {record["original_test_id"]} · {record["fuel"]} · reported {record["test_end"]}')
    actions = {
        "records": (("Compare values", "compare"), ("Ask about this test", "assistant"),
                    ("Open droplet model", "effect")),
        "compare": (("Inspect measurements", "records"), ("Ask about this test", "assistant"),
                    ("Explore solutions", "lab")),
        "assistant": (("Inspect measurements", "records"), ("Explore solutions", "lab"),
                      ("Open droplet model", "effect")),
        "lab": (("Inspect measurements", "records"), ("Ask about this test", "assistant"),
                ("Open droplet model", "effect")),
        "effect": (("Inspect measurements", "records"), ("Compare values", "compare"),
                   ("Ask about this test", "assistant")),
    }
    available = actions[workspace]
    columns = st.columns(len(available))
    for column, (label, target) in zip(columns, available):
        with column:
            if st.button(label, key=f"journey_{workspace}_{target}", width="stretch"):
                follow_experiment(experiment_id, destination=target)


def explorer():
    try:
        store = ResearchStore()
        audit = validate_database(store)
    except (OSError, ResearchError, ValueError) as exc:
        st.error(f"Verified research database unavailable: {exc}")
        st.stop()
    with store:
        copy, art = st.columns([1.05, 1], gap="large", vertical_alignment="center")
        with copy:
            html('<div class="hero-copy"><div class="eyebrow">NASA SPACE APPS CHALLENGE 2026 · RESEARCH EXPLORER</div><h1>Flame in<br><span style="color:#f0a16d">Freefall.</span></h1><p class="lede">Explore the evidence behind combustion and fire safety in microgravity. Follow original investigations, examine what was measured, and keep scientific limits in view.</p><span class="smallcaps">DISCOVER / INSPECT / REASON</span></div>')
        with art:
            html(f'<figure class="hero-art"><img src="data:image/jpeg;base64,{astronaut_data}" alt="NASA International Space Apps Challenge artwork with astronaut"><figcaption>Supplied Space Apps Challenge artwork · original branding preserved</figcaption></figure>')
        html(f'<div class="statusline"><b>VERIFIED RESEARCH</b> &nbsp;·&nbsp; {audit["experiments"]} report-extracted FLEX tests &nbsp;·&nbsp; {audit["passages"]} searchable PDF pages &nbsp;·&nbsp; {audit["documentary_notes"]} documentary notes &nbsp;·&nbsp; {audit["sources"]} catalogued sources</div>')
        example = next((row for row in store.experiments(investigation_id="FLEX", test_query="054", limit=5)
                        if row["original_test_id"].endswith("054")), None)
        if example and st.button("Start with a verified FLEX experiment", type="primary"):
            follow_experiment(example["id"], destination="records")
        st.caption("Suggested path: inspect FLEX test 054, compare its reported measurements, then ask a source-linked question.")
        html('<div class="section-title">Discover research</div>')
        search = st.text_input("Search sources, report pages, and documentary notes", placeholder="Try FLEX, Mir, oxygen, or smoke")
        domains = {row["id"]: row["label"] for row in store.domains()}
        left, middle, right = st.columns(3, gap="small")
        with left:
            domain = st.selectbox("Research domain", [None, *domains], format_func=lambda key: domains.get(key, "All domains"))
        topics = store.topics(domain)
        topic_names = {row["id"]: row["label"] for row in topics}
        with middle:
            topic = st.selectbox("Scientific topic", [None, *topic_names], format_func=lambda key: topic_names.get(key, "All topics"))
            if topic is not None:
                st.session_state["active_topic"] = topic
        investigations = store.investigations(domain)
        investigation_names = {row["id"]: row["name"] for row in investigations}
        with right:
            investigation = st.selectbox("Investigation", [None, *investigation_names],
                                         format_func=lambda key: investigation_names.get(key, "All investigations"))
            if investigation is not None:
                st.session_state["active_investigation"] = investigation

        if investigations:
            html('<div class="section-title">Investigation availability</div>')
            availability = pd.DataFrame([
                {
                    "Investigation": row["name"],
                    "Validated numerical tests": row["admitted_experiments"],
                    "Searchable PDF pages": row["admitted_passages"],
                    "Coverage": "Numerical + documentary" if row["admitted_experiments"]
                                else "Documentary only" if row["admitted_passages"]
                                else "Catalogue / objective summary",
                }
                for row in investigations
            ])
            st.dataframe(availability, hide_index=True, width="stretch")
        else:
            st.caption("This domain contains background or reference sources without named experiment records.")
        if investigation is not None:
            coverage = store.coverage(investigation)
            st.caption(coverage["coverage_note"])
            if coverage["admitted_experiments"]:
                if st.button(f"Open {investigation} experiments", type="primary"):
                    st.session_state["records_investigation"] = investigation
                    st.session_state["active_investigation"] = investigation
                    st.switch_page(pages[1])

        hits = []
        documentary_hits = []
        if search.strip():
            try:
                if domain in (None, "combustion", "detection"):
                    hits = store.passages(search.strip(), investigation_id=investigation, topic_id=topic, limit=5)
                if investigation is None and domain in (None, "historical", "background", "transfer"):
                    documentary_hits = store.documentary_notes(search.strip(), domain_id=domain,
                                                                 topic_id=topic, limit=5)
            except ResearchError as exc:
                st.warning(str(exc))
        sources = store.sources(investigation_id=investigation, domain_id=domain, topic_id=topic)
        if search.strip():
            query = search.strip().casefold()
            hit_urls = {hit["source_url"] for hit in [*hits, *documentary_hits]}
            sources = [item for item in sources if query in item["title"].casefold()
                       or query in (item["identifier"] or "").casefold()
                       or item["url"] in hit_urls]
        html('<div class="section-title">Source catalogue</div>')
        if sources:
            st.dataframe(pd.DataFrame([
                {
                    "Source": item["title"],
                    "Investigation": item["investigation_id"] or "—",
                    "Kind": SOURCE_LABELS.get(item["source_type"], item["source_type"].replace("_", " ").title()),
                    "Verification": SOURCE_LABELS.get(item["verification_status"], item["verification_status"].replace("_", " ").title()),
                    "Availability": SOURCE_LABELS.get(item["admission_status"], item["admission_status"].replace("_", " ").title()),
                }
                for item in sources
            ]), hide_index=True, width="stretch")
            by_key = {item["key"]: item for item in sources}
            chosen = st.selectbox("Inspect a source", list(by_key),
                                  format_func=lambda key: f'{by_key[key]["title"]} · {key}')
            source = by_key[chosen]
            detail, action = st.columns([2, 1], gap="large")
            with detail:
                st.markdown(f'**{source["title"]}**')
                st.caption(f'Identifier: {source["identifier"] or "Not supplied"} · Publisher: {source["publisher"]}')
                with st.expander("Verification, rights and source status"):
                    st.caption(f'Verification: {source["verification_status"]} · Rights: {source["rights_status"]} · Admission: {source["admission_status"]}')
                for evidence in store.source_evidence(chosen):
                    st.write(f'{evidence["source_location"]}: {evidence["summary"]}')
                for note in store.documentary_notes(source_key=chosen):
                    st.write(f'{note["source_location"]}: {note["summary"]}')
            with action:
                st.link_button("Open original source", source["url"])
        else:
            st.info("No catalogued source matches these filters. This does not imply a negative experimental result.")

        if search.strip():
            html('<div class="section-title">Matching report pages</div>')
            if hits:
                for hit in hits:
                    with st.expander(f'{hit["source_title"]} · PDF page {hit["page"]}'):
                        st.write(hit["excerpt"])
                        st.link_button("Open source record", hit["source_url"])
                        st.caption("PDF text supports discovery; verify numerical details against the printed table.")
            elif not documentary_hits:
                st.caption("No approved PDF passage matches the current search and scope.")
            if documentary_hits:
                html('<div class="section-title">Matching documentary evidence</div>')
                for note in documentary_hits:
                    with st.expander(f'{note["source_title"]} · {note["source_location"]}'):
                        st.write(note["summary"])
                        st.caption(f'Factual paraphrase · {note["rights_basis"]} · checked {note["checked_on"]}')
                        st.link_button("Open official source", note["source_url"])
        st.caption("NASA is a research source; it does not operate or endorse this independent dashboard.")


def records():
    heading("01 / SOURCE RECORDS", "Research Records",
            "Inspect validated original test IDs, conditions, measurements, units, and NASA report provenance.")
    try:
        store = ResearchStore()
        validate_database(store)
    except (OSError, ResearchError, ValueError) as exc:
        st.error(f"Verified research database unavailable: {exc}")
        st.stop()
    with store:
        coverage = store.investigations()
        ids = [row["id"] for row in coverage]
        requested = st.session_state.pop("records_investigation", None)
        if requested in ids:
            st.session_state["record_family"] = requested
        elif "record_family" not in st.session_state and st.session_state.get("active_investigation") in ids:
            st.session_state["record_family"] = st.session_state["active_investigation"]
        st.session_state.setdefault("record_family", "FLEX")
        investigation = st.selectbox("Investigation", ids, key="record_family")
        st.session_state["active_investigation"] = investigation
        if investigation != "FLEX":
            st.session_state.pop("active_experiment", None)
        scope = store.coverage(investigation)
        st.caption(scope["coverage_note"])

        if scope["admitted_experiments"]:
            target = st.session_state.pop("record_target", None)
            if target:
                record_target = store.experiment(target)
                if record_target["investigation_id"] == investigation and record_target["validation_status"] == "VALIDATED":
                    st.session_state["record_query"] = record_target["original_test_id"]
                    st.session_state["record_fuel"] = "All fuels"
                    st.session_state["record_oxygen_on"] = False
                    st.session_state["record_pressure_on"] = False
                    st.session_state["record_choice"] = target
            html('<div class="section-title">Filter verified experiments</div>')
            search, fuel_col, measure_col = st.columns([1.4, 1, 1.3], gap="small")
            with search:
                test_query = st.text_input("Test ID contains", placeholder="Example: FLEX–130", key="record_query")
            with fuel_col:
                fuel = st.selectbox("Fuel", ["All fuels", *store.fuels(investigation)], key="record_fuel")
            variable_names = MEASURE_LABELS
            with measure_col:
                variable = st.selectbox("Measurement column", list(variable_names),
                                        format_func=lambda key: variable_names[key])
            oxygen_filter, pressure_filter = st.columns(2, gap="medium")
            with oxygen_filter:
                use_oxygen = st.checkbox("Filter oxygen mole fraction", key="record_oxygen_on")
                oxygen_range = st.slider("O₂ mole fraction", 0.0, 1.0, (0.12, 0.34), 0.01,
                                         disabled=not use_oxygen)
            with pressure_filter:
                use_pressure = st.checkbox("Filter pressure (mmHg)", key="record_pressure_on")
                pressure_range = st.slider("Pressure · mmHg", 0.0, 2400.0,
                                           (500.0, 2350.0), 10.0, disabled=not use_pressure)
            try:
                matches = store.experiments(
                    investigation_id=investigation,
                    fuel=None if fuel == "All fuels" else fuel,
                    test_query=test_query,
                    oxygen_min=oxygen_range[0] if use_oxygen else None,
                    oxygen_max=oxygen_range[1] if use_oxygen else None,
                    pressure_min=pressure_range[0] if use_pressure else None,
                    pressure_max=pressure_range[1] if use_pressure else None,
                    measurement_variable=variable, limit=500,
                )
            except ResearchError as exc:
                st.error(str(exc))
                matches = []
            st.caption(f'{len(matches)} validated tests match · data origin: NASA_REPORT_EXTRACTED · Table IX subset')
            if matches:
                page_size = 50
                total_pages = (len(matches) + page_size - 1) // page_size
                page = st.number_input("Result page", min_value=1, max_value=total_pages, value=1)
                visible = matches[(page - 1) * page_size:page * page_size]
                def record_row(row):
                    token = row["measurement_original"]
                    status = ("Unavailable" if row["measurement_classification"] == "UNAVAILABLE"
                              else "Approximate" if token.lstrip().startswith(("~", "≈"))
                              else row["measurement_classification"].title())
                    return {
                        "Test ID": row["original_test_id"],
                        "Fuel": row["fuel"],
                        "O₂ fraction": row["oxygen_mole_fraction"],
                        "Pressure (mmHg)": row["pressure_mmhg"],
                        variable_names[variable]: (
                            f"Unavailable ({token})" if row["measurement_classification"] == "UNAVAILABLE"
                            else f'{token} {row["measurement_unit"]}'
                        ),
                        "Value status": status,
                        "Outcome (reported)": row["test_end"],
                        "PDF page": row["measurement_page"],
                    }
                table_rows = [record_row(row) for row in visible]
                st.dataframe(pd.DataFrame(table_rows), hide_index=True, width="stretch")
                if all(row["source_rights"] == "Public Use Permitted" for row in matches):
                    st.download_button(
                        "Download filtered measurements (CSV)",
                        pd.DataFrame([record_row(row) for row in matches]).to_csv(index=False).encode("utf-8"),
                        file_name="flex_verified_table_ix_subset.csv", mime="text/csv",
                    )
                    st.caption(f"CSV contains all {len(matches)} filtered, report-extracted records.")
                html('<div class="section-title">Experiment detail</div>')
                choices = {row["id"]: row["original_test_id"] for row in visible}
                if st.session_state.get("record_choice") not in choices:
                    st.session_state.pop("record_choice", None)
                chosen = st.selectbox("Inspect a test", list(choices),
                                      format_func=lambda key: choices[key], key="record_choice")
                st.session_state["active_experiment"] = chosen
                experiment = store.experiment(chosen)
                provenance = store.provenance(chosen)
                a, b = st.columns([1.5, 1], gap="large")
                with a:
                    st.markdown(f'**{experiment["original_test_id"]} · {experiment["fuel"]} · {experiment["test_end"]}**')
                    st.caption(f'Reported test outcome · {experiment["test_date"]} at {experiment["gmt"]} GMT')
                    key_measurements = {measure["variable"]: measure for measure in experiment["measurements"]}
                    summary = st.columns(3)
                    for column, variable in zip(summary, ("initial_diameter_mm", "burning_rate_mm2_s", "burn_time_s")):
                        measure = key_measurements[variable]
                        value = ("Unavailable" if measure["classification"] == "UNAVAILABLE"
                                 else f'{measure["original_value"]} {measure["original_unit"]}')
                        column.metric(MEASURE_LABELS[variable].split(" · ")[0], value)
                    measurement_rows = []
                    for measure in experiment["measurements"]:
                        token = measure["original_value"]
                        status = ("Unavailable" if measure["classification"] == "UNAVAILABLE"
                                  else "Approximate" if token.lstrip().startswith(("~", "≈"))
                                  else measure["classification"].title())
                        measurement_rows.append({
                            "Field": variable_names[measure["variable"]],
                            "Source value": token,
                            "Original unit": measure["original_unit"],
                            "Status": status,
                            "Uncertainty": measure["uncertainty"] or "Not reported in Table IX",
                            "PDF page": measure["page"],
                        })
                    with st.expander("All original measurement cells, units and uncertainties"):
                        st.dataframe(pd.DataFrame(measurement_rows), hide_index=True, width="stretch")
                        st.caption("A source dash remains unavailable; no zero or estimate is inserted.")
                with b:
                    st.markdown("**Source provenance**")
                    st.write(provenance["source_title"])
                    st.caption(f'NASA report · PDF page {provenance["first_pdf_page"]} · printed page {provenance["first_pdf_page"] - 6} · Appendix A, Table IX')
                    st.link_button("Open NASA source report", provenance["source_url"])
                    with st.expander("Verification and rights details"):
                        st.caption(f'Data origin: {provenance["data_origin"]} · Validation: {provenance["validation_status"]}')
                        st.caption(f'Rights: {provenance["source_rights"]} · SHA-256: {provenance["source_sha256"]}')
                journey_context(store, "records")
            else:
                st.info("No validated tests match these filters. Adjust the conditions or choose another investigation.")
        else:
            st.info(f'No validated numerical experiments are admitted for {investigation}. Documentary and catalogue coverage is separate.')
            related = store.sources(investigation_id=investigation)
            if related:
                st.dataframe(pd.DataFrame([
                    {"Source": item["title"], "Status": item["verification_status"],
                     "Evidence": item["admission_status"], "URL": item["url"]}
                    for item in related
                ]), hide_index=True, width="stretch")

        html('<div class="editor-head"><div class="section-title" style="margin:0">Read-only SQL</div><span class="smallcaps">APPROVED RESEARCH PROJECTION</span></div>')
        st.caption("Available tables: experiment_records, measurement_records, source_records, research_passages, research_topics, research_domains.")
        default_sql = "SELECT original_test_id, fuel, test_end FROM experiment_records LIMIT 20"
        sql_text = st.text_area("SQL query", value=default_sql, height=125)
        if st.button("Run read-only query"):
            try:
                st.session_state["sql_result"] = RestrictedSQL(store).execute(sql_text)
                st.session_state["sql_text"] = sql_text
                st.session_state.pop("sql_error", None)
            except QueryRejected as exc:
                st.session_state.pop("sql_result", None)
                st.session_state["sql_error"] = str(exc)
                st.session_state["sql_error_query"] = sql_text
        if st.session_state.get("sql_error") and st.session_state.get("sql_error_query") == sql_text:
            st.error(st.session_state["sql_error"])
        result = st.session_state.get("sql_result")
        if result is not None and st.session_state.get("sql_text") == sql_text:
            st.dataframe(pd.DataFrame(result.rows, columns=result.columns), hide_index=True, width="stretch")
            if result.truncated:
                st.warning("Result truncated by the read-only SQL limit.")
            if result.rows:
                st.download_button(
                    "Download approved SQL result (CSV)",
                    pd.DataFrame(result.rows, columns=result.columns).to_csv(index=False).encode("utf-8"),
                    file_name="research_query_result.csv", mime="text/csv",
                )


def compare():
    heading("02 / MEASUREMENT ANALYSIS", "Compare & Analyze",
            "Explore descriptive relationships within the validated FLEX report subset. Every plotted point traces to an original test and PDF page.")
    try:
        store = ResearchStore()
        validate_database(store)
    except (OSError, ResearchError, ValueError) as exc:
        st.error(f"Verified research database unavailable: {exc}")
        st.stop()
    with store:
        st.session_state["active_investigation"] = "FLEX"
        journey_context(store, "compare")
        st.caption("Scope: FLEX · NASA/TP-2015-216046 Appendix A, Table IX · NASA_REPORT_EXTRACTED · historical report values, not live telemetry")
        labels = {
            "pressure_mmhg": "Atmospheric pressure",
            "oxygen_mole_fraction": "Oxygen mole fraction",
            "nitrogen_mole_fraction": "Nitrogen mole fraction",
            "carbon_dioxide_mole_fraction": "Carbon dioxide mole fraction",
            "helium_mole_fraction": "Helium mole fraction",
            "initial_diameter_mm": "Initial droplet diameter",
            "visible_extinction_diameter_mm": "Visible extinction diameter",
            "burning_rate_mm2_s": "Burning-rate constant",
            "burn_time_s": "Burn duration",
        }
        conditions, axes = st.columns([1, 1], gap="large")
        compare_target = st.session_state.pop("compare_target", None)
        if compare_target:
            st.session_state["compare_fuel"] = "All fuels"
            st.session_state["compare_oxygen_on"] = False
            st.session_state["compare_pressure_on"] = False
            st.session_state["compare_tests"] = [compare_target]
        with conditions:
            html('<div class="section-title">Experimental conditions</div>')
            fuel = st.selectbox("Fuel", ["All fuels", *store.fuels()], key="compare_fuel")
            use_oxygen = st.checkbox("Limit oxygen mole fraction", key="compare_oxygen_on")
            oxygen_range = st.slider("O₂ mole fraction", 0.0, 1.0, (0.12, 0.34), 0.01,
                                     disabled=not use_oxygen, key="compare_oxygen")
            use_pressure = st.checkbox("Limit pressure", key="compare_pressure_on")
            pressure_range = st.slider("Atmospheric pressure · mmHg", 0.0, 2400.0,
                                       (500.0, 2350.0), 10.0, disabled=not use_pressure,
                                       key="compare_pressure")
        with axes:
            html('<div class="section-title">Measurement axes</div>')
            x_var = st.selectbox("Horizontal measurement", list(labels),
                                 index=list(labels).index("initial_diameter_mm"),
                                 format_func=lambda key: labels[key])
            y_var = st.selectbox("Vertical measurement", list(labels),
                                 index=list(labels).index("burn_time_s"),
                                 format_func=lambda key: labels[key])
            st.caption("Axis units are the original report units. Missing cells are excluded from plots and counted below.")
        available = store.experiments(
            investigation_id="FLEX", fuel=None if fuel == "All fuels" else fuel,
            oxygen_min=oxygen_range[0] if use_oxygen else None,
            oxygen_max=oxygen_range[1] if use_oxygen else None,
            pressure_min=pressure_range[0] if use_pressure else None,
            pressure_max=pressure_range[1] if use_pressure else None, limit=500,
        )
        names = {row["id"]: row["original_test_id"] for row in available}
        if "compare_tests" in st.session_state:
            st.session_state["compare_tests"] = [key for key in st.session_state["compare_tests"] if key in names]
        selected = st.multiselect("Limit to specific FLEX tests (optional)", list(names),
                                  format_func=lambda key: names[key],
                                  placeholder="All matching validated tests", key="compare_tests")
        if selected:
            st.session_state["active_experiment"] = selected[-1]
        if x_var == y_var:
            st.info("Choose different measurements for the horizontal and vertical axes.")
            return
        try:
            comparison = build_comparison(
                store, x_var, y_var, fuel=None if fuel == "All fuels" else fuel,
                oxygen_range=oxygen_range if use_oxygen else None,
                pressure_range=pressure_range if use_pressure else None,
                experiment_ids=selected or None,
            )
        except ResearchError as exc:
            st.error(str(exc))
            return
        if comparison.rows.empty:
            st.info("No validated FLEX tests match these conditions.")
            return

        m1, m2, m3 = st.columns(3)
        m1.metric("Selected tests", len(comparison.rows))
        m2.metric("Plotted pairs", len(comparison.plotted))
        m3.metric("Missing either axis", comparison.missing_either)
        st.caption(f"Unavailable horizontal values: {comparison.missing_x} · unavailable vertical values: {comparison.missing_y}. A pair missing both is counted once in the plot exclusion.")
        html('<div class="section-title">Measurement relationship</div>')
        if comparison.plotted.empty:
            st.info("No selected test has both measurements available, so no chart is drawn.")
        else:
            plot = comparison.plotted.copy()
            plot["x_status"] = plot["x_classification"]
            plot["y_status"] = plot["y_classification"]
            figure = px.scatter(
                plot, x="x_numeric_value", y="y_numeric_value", color="fuel",
                symbol="test_end", color_discrete_sequence=["#72dce2", "#f2a16e", "#9ca9ff", "#b5dc8c"],
                hover_name="original_test_id",
                hover_data={"fuel": True, "test_end": True, "oxygen_mole_fraction": ":.3f",
                            "pressure_mmhg": ":.1f", "x_original_value": True,
                            "y_original_value": True, "x_status": True, "y_status": True,
                            "x_page": True, "y_page": True,
                            "x_numeric_value": False, "y_numeric_value": False},
                labels={"x_numeric_value": f"{labels[x_var]} ({comparison.x_unit})",
                        "y_numeric_value": f"{labels[y_var]} ({comparison.y_unit})",
                        "fuel": "Fuel", "test_end": "Reported outcome",
                        "oxygen_mole_fraction": "O₂ mole fraction",
                        "pressure_mmhg": "Pressure (mmHg)",
                        "x_original_value": "Original X token", "y_original_value": "Original Y token",
                        "x_status": "X classification", "y_status": "Y classification",
                        "x_page": "X PDF page", "y_page": "Y PDF page"},
            )
            figure.update_layout(template="plotly_dark", paper_bgcolor="#142127", plot_bgcolor="#142127",
                                 font_color="#dbe9ec", legend_title_text="Fuel / reported outcome",
                                 margin=dict(l=20, r=20, t=25, b=20), height=500)
            figure.update_xaxes(gridcolor="#304750", zerolinecolor="#405660")
            figure.update_yaxes(gridcolor="#304750", zerolinecolor="#405660")
            st.plotly_chart(figure, width="stretch")
            st.caption("Descriptive scatter of reported values only. Colour groups fuels; symbols show the report's test outcome. No causal fit or prediction is implied.")

            html('<div class="section-title">Distribution by fuel</div>')
            if len(plot) >= 3:
                distribution = px.box(plot, x="fuel", y="y_numeric_value", color="fuel",
                                  color_discrete_sequence=["#72dce2", "#f2a16e", "#9ca9ff", "#b5dc8c"],
                                  labels={"fuel": "Fuel", "y_numeric_value": f"{labels[y_var]} ({comparison.y_unit})"})
                distribution.update_layout(template="plotly_dark", paper_bgcolor="#142127", plot_bgcolor="#142127",
                                       font_color="#dbe9ec", showlegend=False,
                                       margin=dict(l=20, r=20, t=25, b=20), height=340)
                distribution.update_yaxes(gridcolor="#304750", zerolinecolor="#405660")
                st.plotly_chart(distribution, width="stretch")
                st.caption("Box summaries are calculated from the plotted subset with Pandas and Plotly; they are not values printed in the NASA report.")
            else:
                st.caption("Choose at least three plotted tests to see a distribution summary.")

        html('<div class="section-title">Comparability and limits</div>')
        differences = []
        if len(comparison.fuels) > 1:
            differences.append(f"Fuels differ: {', '.join(comparison.fuels)}.")
        if comparison.oxygen_span and comparison.oxygen_span[0] != comparison.oxygen_span[1]:
            differences.append(f"O₂ mole fraction ranges from {comparison.oxygen_span[0]:.3f} to {comparison.oxygen_span[1]:.3f}.")
        if comparison.pressure_span and comparison.pressure_span[0] != comparison.pressure_span[1]:
            differences.append(f"Pressure ranges from {comparison.pressure_span[0]:.1f} to {comparison.pressure_span[1]:.1f} mmHg.")
        if differences:
            st.warning("Selected tests differ in experimental conditions. " + " ".join(differences)
                       + " Inspect individual tests before drawing scientific conclusions.")
        else:
            st.info("Fuel, oxygen fraction and pressure are uniform in this selection; other experimental differences may remain.")
        st.caption("MEASURED and DERIVED are the transcription's source classifications. No uncertainty is displayed as an error bar unless the report supplies a numerical uncertainty for that cell.")

        html('<div class="section-title">Trace every point</div>')
        trace = comparison.rows[["original_test_id", "fuel", "test_end", "oxygen_mole_fraction",
                                 "pressure_mmhg", "x_original_value", "x_original_unit",
                                 "x_classification", "x_uncertainty", "x_page",
                                 "y_original_value", "y_original_unit", "y_classification",
                                 "y_uncertainty", "y_page", "source_title", "source_url"]].copy()
        trace.columns = ["Test ID", "Fuel", "Reported outcome", "O₂ fraction", "Pressure (mmHg)",
                         "Horizontal source value", "Horizontal unit", "Horizontal status",
                         "Horizontal uncertainty", "Horizontal PDF page", "Vertical source value",
                         "Vertical unit", "Vertical status", "Vertical uncertainty",
                         "Vertical PDF page", "NASA report", "Source URL"]
        trace = trace.fillna({"Horizontal uncertainty": "Not reported", "Vertical uncertainty": "Not reported"})
        st.dataframe(trace, hide_index=True, width="stretch")
        st.link_button("Open NASA report", comparison.rows.iloc[0]["source_url"])
        st.caption("A dash in an original value remains unavailable. Each row preserves its original token, unit, classification and PDF page.")


def load_evidence(question, investigation=None, domain=None, topic=None):
    """Retrieve public evidence per request without caching visitors' questions."""
    with ResearchStore() as store:
        return retrieve_evidence(store, question, investigation_id=investigation,
                                 domain_id=domain, topic_id=topic)


@st.cache_resource(show_spinner=False)
def ai_adapter():
    return GroqAdapter(load_groq_settings())


def optional_answer(packet, *, history=()):
    """One shared provider boundary and request budget for both research workspaces."""
    used = st.session_state.get("ai_request_count", 0)
    result, new_used = research_turn(packet, ai_adapter(), used, history=history)
    st.session_state["ai_request_count"] = new_used
    return result


def answer_status(result, *, show_evidence_summary=True):
    if result.mode == "model":
        st.caption("AI explanation · automated citation and value checks passed; review the original sources below.")
        for claim in result.claims:
            st.write(claim)
        return
    messages = {
        "missing_key": "Generative mode is unavailable here. Verified source evidence remains available; visitors do not need an API key.",
        "missing_evidence": "The approved corpus cannot support a factual answer to this question yet.",
        "no_safe_evidence": "No safe source excerpt was available for generation.",
        "session_limit": "This session has reached its AI request limit. Verified evidence remains available.",
        "rate_limited": "The AI provider is rate limited. Showing verified evidence instead.",
        "authentication_failed": "The AI provider is unavailable due to configuration. Showing verified evidence instead.",
        "provider_unavailable": "The AI provider is temporarily unavailable. Showing verified evidence instead.",
        "claim_validation_failed": "The generated answer did not pass source checks. Showing verified evidence instead.",
        "empty_response": "The AI provider returned no answer. Showing verified evidence instead.",
    }
    st.info(messages.get(result.status, "Showing verified evidence without a generated answer."))
    if show_evidence_summary:
        evidence_summary(result.evidence_packet)


def supporting_citations(result):
    if not result.citations:
        st.caption("No generated claims were admitted. Inspect the verified evidence records below.")
        return
    for item in result.citations:
        st.write(f'[{item["id"]}] {item["source_title"]} · {item["location"]}' +
                 (f' · {item["experiment_id"]}' if item.get("experiment_id") else ""))
        st.link_button(f'Open source {item["id"]}', item["source_url"])


def evidence_summary(packet):
    route = packet["route"]
    st.caption(f'DETERMINISTIC EVIDENCE SUMMARY · {route["domain"].upper()} · {route["intent"].upper()} · not an LLM-generated answer')
    if packet["supported"]:
        count = sum(item["kind"] != "source_pointer" for item in packet["items"])
        if all(item["kind"] == "documentary_note" for item in packet["items"]):
            st.write(f"Found {count} admitted documentary note(s). Inspect each official source in the evidence panel; these are factual summaries, not experiment measurements.")
        else:
            st.write(f"Found {count} admitted evidence item(s) in the selected scope. Read the source excerpts and original measurements below; they are not a causal conclusion.")
    for note in packet["notices"]:
        st.warning(note)
    for expansion in packet["expansions"]:
        st.caption("Scope expansion: " + expansion)
    if packet["scopes"]:
        st.caption("Investigations searched separately: " + ", ".join(packet["scopes"]))


def evidence_items(packet, *, compact=False):
    for index, item in enumerate(packet["items"], 1):
        title = f'{index}. {item["source_title"]} · {item["location"]}'
        with st.expander(title, expanded=not compact and index == 1):
            st.caption(f'{item["kind"].replace("_", " ").title()} · Identifier: {item["source_identifier"]} · Investigation: {item["investigation_id"] or "none"} · Verification: {item["verification_status"]}')
            if item["experiment_id"]:
                st.write(f'Original test: **{item["experiment_id"]}**')
            st.write(item["text"])
            if item["measurements"]:
                st.dataframe(pd.DataFrame([{
                    "Field": m["variable"], "Original value": m["original_value"],
                    "Original unit": m["original_unit"], "Classification": m["classification"],
                    "Uncertainty": m["uncertainty"] or "Not reported", "PDF page": m["page"],
                } for m in item["measurements"]]), hide_index=True, width="stretch")
            st.link_button("Open original NASA source", item["source_url"])


def lab():
    heading("03 / ENGINEERING RESEARCH", "Solution Lab",
            "Frame a fire-safety research question and inspect admitted evidence before recording design considerations.")
    with ResearchStore() as store:
        journey_context(store, "lab")
    question, context = st.columns([1.5, 1], gap="large")
    with question:
        html('<div class="step">01 / DEFINE THE PROBLEM</div>')
        if "lab_problem" not in st.session_state and st.session_state.get("active_question"):
            st.session_state["lab_problem"] = st.session_state["active_question"]
        problem = st.text_area("Research problem", placeholder="Example: What evidence informs oxygen-sensitive flame extinction in FLEX?", height=145, key="lab_problem")
    with context:
        html('<div class="step">02 / SET THE CONTEXT</div>')
        if "lab_investigation" not in st.session_state:
            st.session_state["lab_investigation"] = st.session_state.get("active_investigation")
        investigation = st.selectbox("Investigation focus", [None, "FLEX", "BASS-II", "SAFFIRE", "SAME", "SPICE"],
                                     format_func=lambda key: key or "Route from question", key="lab_investigation")
        st.caption("Only approved passages, objective summaries and validated records are retrieved.")
    if st.button("Gather research evidence", type="primary"):
        try:
            packet = load_evidence(problem, investigation=investigation)
            st.session_state["active_question"] = problem
            with st.spinner("Checking the selected research evidence..."):
                st.session_state["lab_result"] = optional_answer(packet)
            st.session_state["lab_question"] = problem
        except (ResearchError, OSError) as exc:
            st.error(str(exc))
    result = st.session_state.get("lab_result")
    if result is not None:
        packet = result.evidence_packet
        evidence, considerations = st.columns([1.5, 1], gap="large")
        with evidence:
            html('<div class="step">03 / VERIFIED OBSERVATIONS</div>')
            evidence_summary(packet)
            evidence_items(packet, compact=True)
            html('<div class="step">04 / SCIENTIFIC INTERPRETATION</div>')
            answer_status(result, show_evidence_summary=False)
        with considerations:
            html('<div class="step">05 / POSSIBLE ENGINEERING DIRECTIONS</div>')
            st.write("If the retrieved conditions match the proposed use, consider testing the proposed control under independently reviewed conditions. Identify missing measurements before selecting a design.")
            html('<div class="step">06 / ASSUMPTIONS AND LIMITATIONS</div>')
            st.write("These records cover the admitted research subset. A design would require its own fuel, atmosphere, pressure, apparatus and safety review. No spacecraft certification is implied.")
            for note in packet["notices"]:
                st.caption(note)
            html('<div class="step">07 / SUPPORTING CITATIONS</div>')
            supporting_citations(result)
            st.caption("Problem entered: " + st.session_state.get("lab_question", ""))
    else:
        st.caption("Enter a problem to retrieve source-linked evidence. No engineering solution is generated automatically.")
    st.caption("This research workspace does not certify spacecraft safety decisions.")


def assistant():
    heading("04 / EVIDENCE-LED DIALOGUE", "AI Research Assistant",
            "Ask research questions, inspect original sources, and use optional source-checked explanations when the provider is configured.")
    with ResearchStore() as store:
        journey_context(store, "assistant")
    if not ai_adapter().settings.configured:
        st.info("Generative mode is unavailable without an owner-configured key. Verified evidence mode is ready; visitors do not need an API key.")
    conversation, evidence = st.columns([1.35, 1], gap="large")
    with conversation:
        html('<div class="section-title" style="margin-top:0">Conversation</div>')
        if "research_chat" not in st.session_state:
            st.session_state["research_chat"] = []
        for message in st.session_state["research_chat"][-8:]:
            with st.chat_message(message["role"]):
                if message["role"] == "user":
                    st.write(message["text"])
                else:
                    answer_status(message["result"])
                    st.caption("Open the evidence inspector for source locations and any reported measurement cells.")
        if st.session_state.pop("assistant_target", False):
            st.session_state["assistant_prompt"] = st.session_state.get("active_question", "")
            st.session_state["assistant_scope"] = st.session_state.get("active_investigation")
        prompt = st.text_input("Research question", placeholder="Ask about FLEX, BASS-II, smoke detection, or a specific test", key="assistant_prompt")
        with ResearchStore() as store:
            topic_labels = {row["id"]: row["label"] for row in store.topics()}
        if "assistant_topic" not in st.session_state and st.session_state.get("active_topic") in topic_labels:
            st.session_state["assistant_topic"] = st.session_state["active_topic"]
        scope_col, topic_col = st.columns(2, gap="small")
        with scope_col:
            scope = st.selectbox("Investigation scope", [None, "FLEX", "BASS-II", "SAFFIRE", "SAME", "SPICE"],
                                 format_func=lambda key: key or "Route from question", key="assistant_scope")
        with topic_col:
            topic = st.selectbox("Topic scope", [None, *topic_labels],
                                 format_func=lambda key: topic_labels.get(key, "Route from question"), key="assistant_topic")
        remaining = max(0, ai_adapter().settings.session_request_limit - st.session_state.get("ai_request_count", 0))
        if ai_adapter().settings.configured:
            st.caption(f"AI requests remaining this session: {remaining}")
        if st.button("Ask and inspect", type="primary"):
            try:
                packet = load_evidence(prompt, investigation=scope, topic=topic)
                st.session_state["active_question"] = prompt
                if topic is not None:
                    st.session_state["active_topic"] = topic
                history = tuple(m["text"] for m in st.session_state["research_chat"] if m["role"] == "user")[-2:]
                with st.spinner("Retrieving and checking source evidence..."):
                    result = optional_answer(packet, history=history)
                st.session_state["research_chat"].extend([
                    {"role": "user", "text": prompt}, {"role": "assistant", "result": result},
                ])
                st.session_state["research_chat"] = st.session_state["research_chat"][-12:]
                st.rerun()
            except (ResearchError, OSError) as exc:
                st.error(str(exc))
    with evidence:
        html('<div class="section-title" style="margin-top:0">Evidence inspector</div>')
        latest = next((m["result"] for m in reversed(st.session_state.get("research_chat", []))
                       if m["role"] == "assistant"), None)
        if latest:
            supporting_citations(latest)
            evidence_items(latest.evidence_packet, compact=True)
        else:
            st.caption("Ask a question to see source citations, PDF pages and original measurements here.")


def simulation_player(model):
    """One small independently rerun view; all values come from DropletModel."""
    end = model.ideal_zero_time_s
    if st.session_state.get("sim_playing"):
        st.session_state["sim_time_s"] = min(end, st.session_state["sim_time_s"] + end / 90)
        if st.session_state["sim_time_s"] >= end:
            st.session_state["sim_playing"] = False
            st.rerun()
    t = min(st.session_state.get("sim_time_s", 0.0), end)
    diameter = model.diameter_mm(t)
    play, pause, reset = st.columns(3)
    if play.button("▶ Play", key="sim_play", disabled=st.session_state.get("sim_playing", False), width="stretch"):
        if t >= end:
            st.session_state["sim_time_s"] = 0.0
        st.session_state["sim_playing"] = True
        st.rerun()
    if pause.button("Ⅱ Pause", key="sim_pause", disabled=not st.session_state.get("sim_playing", False), width="stretch"):
        st.session_state["sim_playing"] = False
        st.rerun()
    if reset.button("↺ Reset", key="sim_reset", width="stretch"):
        st.session_state["sim_playing"] = False
        st.session_state["sim_time_s"] = 0.0
        st.rerun()
    diameter_px = max(5, round(160 * diameter / model.initial_diameter_mm))
    html(f'<div class="droplet-stage" role="img" aria-label="Schematic predicted droplet diameter {diameter:.2f} millimeters"><div class="droplet" style="width:{diameter_px}px;height:{diameter_px}px"></div></div>')
    st.caption("Schematic droplet size · cyan circle represents predicted liquid diameter, not a flame or measured image.")
    current, elapsed, ideal = st.columns(3)
    current.metric("Predicted diameter", f"{diameter:.2f} mm")
    elapsed.metric("Model elapsed time", f"{t:.1f} s")
    ideal.metric("Ideal D = 0 time", f"{end:.1f} s")
    profile = model.profile()
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=[point[0] for point in profile], y=[point[1] for point in profile],
                                mode="lines", name="D-squared model", line=dict(color="#72dce2", width=3)))
    figure.add_trace(go.Scatter(x=[t], y=[diameter], mode="markers", name="Current model state",
                                marker=dict(color="#f2a16e", size=12)))
    figure.update_layout(template="plotly_dark", paper_bgcolor="#142127", plot_bgcolor="#142127",
                         font_color="#dbe9ec", height=340, margin=dict(l=25, r=15, t=25, b=20),
                         xaxis_title="Model elapsed time (s)", yaxis_title="Predicted droplet diameter (mm)",
                         showlegend=True)
    figure.update_xaxes(range=[0, end], gridcolor="#304750")
    figure.update_yaxes(range=[0, model.initial_diameter_mm * 1.08], gridcolor="#304750")
    st.plotly_chart(figure, width="stretch", key="sim_diameter_chart")


def illustrative_inputs():
    st.session_state["sim_mode"] = "illustrative"
    st.session_state.pop("sim_source_id", None)
    st.session_state["sim_playing"] = False
    st.session_state["sim_time_s"] = 0.0


def effect():
    heading("05 / MODEL & VISUAL CONTEXT", "View Effect", "Explore a bounded droplet-size model while keeping the supplied artwork, NASA measurements, and calculated values distinct.")
    html(f'<div class="effect-stage"><div class="effect-art"><img src="data:image/png;base64,{flame_data}" alt="Flame suspended above the curve of Earth"></div><div class="effect-label">Supplied flame-over-Earth artwork · conceptual visual, not experimental footage</div></div>')
    control, context = st.columns([1, 1.3], gap="large")
    try:
        with ResearchStore() as store:
            tests = store.experiments(investigation_id="FLEX", limit=500)
            by_id = {row["id"]: row for row in tests}
            target = st.session_state.pop("effect_target", None)
            if target in by_id:
                st.session_state["effect_choice"] = target
            with control:
                html('<div class="section-title" style="margin-top:0">Verified test context</div>')
                chosen = st.selectbox("Inspect a FLEX test", list(by_id),
                                      format_func=lambda key: by_id[key]["original_test_id"], key="effect_choice")
                st.session_state["active_investigation"] = "FLEX"
                st.session_state["active_experiment"] = chosen
                row = by_id[chosen]
                st.write(f'**{row["original_test_id"]} · {row["fuel"]}**')
                st.caption(f'O₂ mole fraction {row["oxygen_mole_fraction"]} · pressure {row["pressure_mmhg"]} mmHg · reported outcome {row["test_end"]}')
                st.link_button("NASA report and source record", row["source_url"])
                record = store.experiment(chosen)
                source_inputs = compatible_report_inputs(record)
                if source_inputs:
                    if st.button("Load this test's D₀ and K into model", type="primary"):
                        st.session_state["sim_initial_mm"] = source_inputs.initial_diameter_mm
                        st.session_state["sim_rate_mm2_s"] = source_inputs.burning_rate_mm2_s
                        st.session_state["sim_source_id"] = chosen
                        st.session_state["sim_mode"] = "source"
                        st.session_state["sim_playing"] = False
                        st.session_state["sim_time_s"] = 0.0
                        st.rerun()
                else:
                    st.info("This test lacks a validated positive diameter and burning-rate pair in the required units; use illustrative model inputs below.")
            with context:
                html('<div class="section-title" style="margin-top:0">Research evidence</div>')
                number = row["original_test_id"][-3:]
                packet = load_evidence(f"What measurements and outcome did FLEX test {number} report?", investigation="FLEX")
                evidence_items({**packet, "items": [item for item in packet["items"]
                                                      if item.get("experiment_id") == row["original_test_id"]]}, compact=True)
                st.caption("The artwork does not depict the selected test. The model below calculates only liquid droplet diameter; it does not reproduce flame appearance.")
            journey_context(store, "effect")
            html('<div class="section-title">D-squared droplet model</div>')
            st.write("D(t)² = D₀² − Kt. A constant positive burning-rate parameter K makes the model droplet diameter shrink until its ideal zero-diameter time. It does not predict flame extinction, oxygen response, or spacecraft fire behavior.")
            if st.session_state.get("sim_mode") == "source" and st.session_state.get("sim_source_id") != chosen:
                st.session_state["sim_initial_mm"] = 3.0
                st.session_state["sim_rate_mm2_s"] = 0.4
                illustrative_inputs()
            st.session_state.setdefault("sim_initial_mm", 3.0)
            st.session_state.setdefault("sim_rate_mm2_s", 0.4)
            inputs, display = st.columns([1, 1.3], gap="large")
            with inputs:
                st.slider("Initial droplet diameter D₀ (mm)", 0.5, 5.0, step=0.01,
                          key="sim_initial_mm", on_change=illustrative_inputs)
                st.slider("Burning-rate parameter K (mm²/s)", 0.05, 1.2, step=0.01,
                          key="sim_rate_mm2_s", on_change=illustrative_inputs)
                if st.session_state.get("sim_mode") == "source" and source_inputs:
                    st.success(f'Source-derived inputs: {source_inputs.original_test_id} · D₀ {source_inputs.diameter_original} mm ({source_inputs.diameter_classification}, PDF p. {source_inputs.diameter_pdf_page}); K {source_inputs.rate_original} mm²/s ({source_inputs.rate_classification}, PDF p. {source_inputs.rate_pdf_page}).')
                    reported_duration = (f"{source_inputs.reported_burn_duration} s" if source_inputs.reported_burn_duration
                                         else "unavailable")
                    st.caption(f'NASA report separately records {source_inputs.reported_outcome} and burn duration {reported_duration}. These are observations, not model outputs.')
                    st.link_button("Inspect source of loaded inputs", source_inputs.source_url)
                else:
                    st.info("Illustrative inputs. These slider values are examples; no NASA test is claimed to have used them.")
                st.caption("NASA defines D₀ at igniter-on and fits K from shortly after ignition to extinction. Their time origins differ, so a source-loaded curve is a teaching approximation, not a reconstruction of the observed trajectory.")
            model = DropletModel(st.session_state["sim_initial_mm"], st.session_state["sim_rate_mm2_s"])
            signature = (model.initial_diameter_mm, model.burning_rate_mm2_s)
            if st.session_state.get("sim_signature") != signature:
                st.session_state["sim_signature"] = signature
                st.session_state["sim_time_s"] = 0.0
                st.session_state["sim_playing"] = False
            with display:
                st.fragment(simulation_player, run_every="0.2s" if st.session_state.get("sim_playing") else None)(model)
            st.caption("Model zero-diameter time is D₀²/K, a mathematical endpoint only. The chart and schematic are calculated from the same Python model; no results are written to SQLite.")
    except (OSError, ResearchError, ValueError) as exc:
        st.error(f"Research context unavailable: {exc}")


import base64

astronaut_data = base64.b64encode(ASTRONAUT.read_bytes()).decode("ascii")
flame_data = base64.b64encode(FLAME.read_bytes()).decode("ascii")
st.sidebar.markdown('<div class="sidebrand"><div class="mark">✦</div><strong>FLAME IN FREEFALL</strong><small>Microgravity combustion<br>research workspace</small></div>', unsafe_allow_html=True)
pages = [
    st.Page(explorer, title="Research Explorer", icon="🔎", default=True),
    st.Page(records, title="Research Records", icon="📋"),
    st.Page(compare, title="Compare & Analyze", icon="📈"),
    st.Page(lab, title="Solution Lab", icon="🧪"),
    st.Page(assistant, title="AI Research Assistant", icon="💬"),
    st.Page(effect, title="View Effect", icon="🔥"),
]
st.navigation(pages, position="sidebar").run()
