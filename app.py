# Co-authored with ChatGPT
"""Flame in Freefall — Phase 2 visual research interface."""
from pathlib import Path

import streamlit as st

ASSETS = Path(__file__).parent / "assets"
ASTRONAUT = ASSETS / "space_apps_astronaut.jpg"
FLAME = ASSETS / "flame_over_earth.png"

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


def explorer():
    copy, art = st.columns([1.05, 1], gap="large", vertical_alignment="center")
    with copy:
        html('<div class="hero-copy"><div class="eyebrow">NASA SPACE APPS CHALLENGE 2026 · RESEARCH EXPLORER</div><h1>Flame in<br><span style="color:#f0a16d">Freefall.</span></h1><p class="lede">Explore the evidence behind combustion and fire safety in microgravity. Follow original investigations, examine what was measured, and keep scientific limits in view.</p><span class="smallcaps">DISCOVER / INSPECT / REASON</span></div>')
    with art:
        html(f'<figure class="hero-art"><img src="data:image/jpeg;base64,{astronaut_data}" alt="NASA International Space Apps Challenge artwork with astronaut"><figcaption>Supplied Space Apps Challenge artwork · original branding preserved</figcaption></figure>')
    html('<div class="statusline"><b>RESEARCH PREVIEW</b> &nbsp;·&nbsp; Six workspaces &nbsp;·&nbsp; Verified source integration pending &nbsp;·&nbsp; Independent Space Apps project</div>')
    html('<div class="section-title">Explore the research</div>')
    st.text_input("Search investigations", placeholder="Search source-linked investigations", disabled=True)
    a, b, c = st.columns(3, gap="medium")
    with a:
        surface("01 / FLAME EXTINCTION", "FLEX", "Liquid-fuel droplet combustion and extinction. A validated report transcription subset is prepared for future integration.", "orange")
    with b:
        surface("02 / MATERIAL BEHAVIOR", "BASS-II", "Solid-fuel behavior under varied geometry and airflow. Experimental records remain in source review.")
    with c:
        surface("03 / FIRE SAFETY", "SAME-R & Saffire", "Smoke detection and spacecraft fire studies. Browse the documented investigation scope.", "orange")
    html('<div class="section-title">Research path</div>')
    a, b, c = st.columns(3, gap="medium")
    with a:
        surface("DISCOVER", "Find an investigation", "Locate a research family and its published source.")
    with b:
        surface("INSPECT", "Read the evidence", "Check test conditions, units, missing values, and provenance.")
    with c:
        surface("INTERPRET", "Compare with care", "Review limitations before drawing engineering conclusions.")
    st.caption("NASA is a research source; it does not operate or endorse this independent dashboard.")


def records():
    heading("01 / SOURCE RECORDS", "Research Records", "A structured view for original test IDs, conditions, measurements, uncertainty, and source provenance.")
    html('<div class="section-title">Record browser</div>')
    search, family, measure = st.columns([2, 1, 1], gap="small")
    with search:
        st.text_input("Find a record", placeholder="Test ID or source keyword", disabled=True)
    with family:
        st.selectbox("Investigation", ["All investigations"], disabled=True)
    with measure:
        st.selectbox("Measurement", ["All fields"], disabled=True)
    table, inspector = st.columns([2.5, 1], gap="large")
    with table:
        html('<div class="table-wrap"><table class="data-table"><thead><tr><th>Investigation</th><th>Test ID</th><th>Fuel / material</th><th>Atmosphere</th><th>Measurement</th><th>Units</th><th>Source page</th></tr></thead><tbody><tr><td colspan="7">Validated experiment rows will appear when the scientific database is connected.</td></tr></tbody></table></div>')
        html('<div class="editor-head"><div class="section-title" style="margin:0">SQL editor</div><span class="smallcaps">READ-ONLY PREVIEW</span></div>')
        html('<div class="code-frame">SELECT test_id, fuel, atmosphere, measurement, unit<br>FROM verified_experiments<br>WHERE investigation_id = :investigation;</div>')
        st.caption("Query execution is disabled in this frontend milestone.")
    with inspector:
        html('<div class="section-title" style="margin-top:.1rem">Experiment detail</div>')
        html('<div class="surface"><span class="smallcaps">NO RECORD SELECTED</span><h3>Source inspector</h3><div class="inspector-line"><span>Original test ID</span><span>—</span></div><div class="inspector-line"><span>Printed page / table</span><span>—</span></div><div class="inspector-line"><span>Uncertainty</span><span>—</span></div><div class="inspector-line"><span>Data origin</span><span>—</span></div><div class="inspector-line"><span>Validation</span><span>—</span></div></div>')
        st.caption("Blank values represent no selected record, not measured zeros.")


def compare():
    heading("02 / MEASUREMENT ANALYSIS", "Compare & Analyze", "A scientific comparison workspace designed to preserve measurement units and experimental context.")
    left, right = st.columns(2, gap="large")
    with left:
        st.selectbox("Reference experiment", ["Select a validated record"], disabled=True)
    with right:
        st.selectbox("Comparison experiment", ["Select a validated record"], disabled=True)
    html('<div class="section-title">Measurement canvas</div>')
    html('<div class="chart-frame"><div class="axis-y">Measured value · original unit</div><div class="chart-empty"><strong>No measurements plotted</strong>Validated source-linked records are required.</div><div class="axis-x">Experiment or condition</div></div>')
    a, b = st.columns([1.35, 1], gap="large")
    with a:
        surface("COMPARISON", "Conditions side by side", "Fuel or material · atmosphere · pressure · apparatus · reported outcome.")
    with b:
        surface("INTERPRETATION", "Compatibility check", "Missing fields, differing methods, and reported uncertainty will be visible before comparison.", "orange")


def lab():
    heading("03 / ENGINEERING RESEARCH", "Solution Lab", "Frame a fire-safety problem, gather relevant evidence, and document design considerations.")
    question, context = st.columns([1.5, 1], gap="large")
    with question:
        html('<div class="step">01 / DEFINE THE PROBLEM</div>')
        st.text_area("Research question", placeholder="Describe the system, hazard, or design question…", height=160, disabled=True)
    with context:
        html('<div class="step">02 / SET THE CONTEXT</div>')
        st.selectbox("Investigation focus", ["Choose a research area"], disabled=True)
        st.selectbox("Environment", ["Choose experimental conditions"], disabled=True)
    evidence, considerations = st.columns(2, gap="large")
    with evidence:
        html('<div class="step">03 / REVIEW EVIDENCE</div>')
        surface("SOURCE-BOUND", "Supporting research", "Source passages, experiment identifiers, conditions, and applicability limits will appear here.")
    with considerations:
        html('<div class="step">04 / DOCUMENT REASONING</div>')
        surface("DESIGN NOTES", "Engineering considerations", "Record assumptions, tradeoffs, open questions, and further tests needed.", "orange")
    st.caption("This research workspace does not certify spacecraft safety decisions.")


def assistant():
    heading("04 / EVIDENCE-LED DIALOGUE", "AI Research Assistant", "A conversation workspace for questions that require traceable research support.")
    conversation, evidence = st.columns([1.65, 1], gap="large")
    with conversation:
        html('<div class="section-title" style="margin-top:0">Conversation</div>')
        html('<div class="chat-window"><div class="chat-msg"><small>RESEARCH ASSISTANT · PREVIEW</small>When source retrieval is connected, ask about an investigation or measurement. Answers will distinguish reported findings from interpretation.</div></div>')
        html('<div class="composer">Ask a question about microgravity combustion… <span>↗</span></div>')
        st.caption("Message submission is unavailable until evidence retrieval is validated.")
    with evidence:
        html('<div class="section-title" style="margin-top:0">Evidence inspector</div>')
        surface("CLAIM TRACE", "No claim selected", "Select a cited statement to inspect the source passage and its scientific context.")
        html('<div class="section-title">Source citations</div>')
        html('<div class="surface"><span class="smallcaps">CITATION REGISTER</span><h3>No citations yet</h3><p>Document, page, and test identifiers will accompany supported answers.</p></div>')


def effect():
    heading("05 / VISUAL CONTEXT", "View Effect", "Examine the visual idea of a flame above Earth while keeping artwork separate from experimental evidence.")
    html(f'<div class="effect-stage"><div class="effect-art"><img src="data:image/png;base64,{flame_data}" alt="Flame suspended above the curve of Earth"></div><div class="effect-label">Supplied flame-over-Earth artwork · conceptual visual, not experimental footage</div></div>')
    control, context = st.columns([1, 1.3], gap="large")
    with control:
        html('<div class="section-title" style="margin-top:0">Scene controls</div>')
        st.selectbox("Research-backed preset", ["Available after source validation"], disabled=True)
        st.caption("No simulation or experimental measurements are shown.")
    with context:
        html('<div class="section-title" style="margin-top:0">Evidence context</div>')
        surface("VISUAL STATUS", "Illustration", "Future research views will identify their fuel, atmosphere, gravity, apparatus, original media source, and limitations.", "orange")


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