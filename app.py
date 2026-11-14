# Co-authored with ChatGPT
"""Flame in Freefall: Phase 2 interface preview."""
from pathlib import Path

import streamlit as st

ASSET = Path(__file__).parent / "assets" / "space_apps_astronaut.jpg"

st.set_page_config(page_title="Flame in Freefall", page_icon="🔥", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif}
h1,h2,h3 {font-family:'Space Grotesk',sans-serif;letter-spacing:-.025em}
[data-testid="stAppViewContainer"] {background:radial-gradient(ellipse at 82% 0%,#143040 0%,transparent 32%),#10171d}
[data-testid="stSidebar"] {background:#0b1117;border-right:1px solid #2a3942}
[data-testid="stSidebar"] [data-testid="stImage"] img {border-radius:8px}
.block-container {max-width:1320px;padding-top:3.5rem}
.eyebrow {color:#70dce7;text-transform:uppercase;letter-spacing:.18em;font-size:.75rem;font-weight:700}
.lede {color:#afc2c9;font-size:1.08rem;max-width:740px;line-height:1.65}
.panel {background:#17232b;border:1px solid #30424c;border-radius:16px;padding:1.2rem 1.35rem;margin:.45rem 0 1rem}
.panel h3 {margin:0 0 .4rem;color:#edf8fa;font-size:1.08rem}
.panel p {margin:0;color:#adc0c8;line-height:1.55}
.tag {display:inline-block;color:#8de0e8;background:#17323a;border:1px solid #2d5961;border-radius:100px;padding:.2rem .7rem;font-size:.74rem;font-weight:700;margin-bottom:.7rem}
.warm {color:#ffad73}
.hero-note {color:#bdcbd0;font-size:.86rem;margin-top:.35rem}
div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {background:#14212a;border:1px solid #38505b;color:#e9f4f5}
div[data-testid="stSelectbox"] > div {background:#14212a}
div.stButton button {border-color:#3a6470;color:#c7f4f2}
div[data-testid="stAlert"] {border-radius:12px}
@media(max-width:750px){.block-container{padding:1rem}.panel{padding:1rem}}
</style>
""", unsafe_allow_html=True)

def heading(kicker, title, intro):
    st.markdown(f'<div class="eyebrow">{kicker}</div>', unsafe_allow_html=True)
    st.title(title)
    st.markdown(f'<p class="lede">{intro}</p>', unsafe_allow_html=True)

def panel(title, body, tag=None):
    badge=f'<span class="tag">{tag}</span><br>' if tag else ''
    st.markdown(f'<div class="panel">{badge}<h3>{title}</h3><p>{body}</p></div>', unsafe_allow_html=True)

def notice(text="Interface preview · Scientific data integration is planned for Phase 3."):
    st.info(text, icon="ℹ️")

def explorer():
    left,right=st.columns([1.1,1],gap="large",vertical_alignment="center")
    with left:
        heading("NASA Space Apps Challenge 2026", "Flame in Freefall", "Explore the evidence behind combustion and fire safety in microgravity. A research workspace built around traceable sources, measured conditions, and clear scientific limits.")
        st.caption("Independent hackathon project by Not Exactly Rocket Science, Is It?! · NASA is a research source, not the operator or endorser of this app.")
    with right:
        st.image(str(ASSET),use_container_width=True)
        st.markdown('<div class="hero-note">Supplied Space Apps Challenge artwork, shown in full to preserve its original lettering.</div>',unsafe_allow_html=True)
    st.divider()
    st.subheader("Find research")
    st.text_input("Search investigations",placeholder="Search will connect to verified research records in Phase 3",disabled=True)
    st.caption("Search is a preview. No results are fabricated.")
    st.segmented_control("Research area",["All","Prevention","Detection","Suppression"],default="All",disabled=True)
    a,b,c=st.columns(3,gap="medium")
    with a: panel("FLEX", "Liquid droplet burning and flame extinction. A validated subset of NASA report Table IX is prepared for later integration.","Suppression")
    with b: panel("BASS-II", "Solid-fuel flammability across material, geometry and airflow conditions. Record-level integration is pending.","Prevention")
    with c: panel("SAME-R & Saffire", "Smoke detection and larger-scale spacecraft fire studies. Source review continues before numerical display.","Detection · Prevention")
    st.subheader("Evidence first")
    panel("Source and provenance", "The current research corpus includes a report-extracted FLEX subset with original units and page references. The research interface will display only validated records after integration.")

def records():
    heading("Research workspace", "Research Records", "Inspect original test identifiers, measurements, units and provenance once the validated database is connected.")
    notice()
    a,b=st.columns([2,1],gap="large")
    with a:
        st.text_input("Filter records",placeholder="Record search arrives with database integration",disabled=True)
        panel("Records table", "Validated experiment rows will appear here with their test ID, conditions, measurements and source page.","Awaiting data connection")
        st.text_area("Read-only SQL workspace",placeholder="SELECT …",disabled=True,height=125)
        st.caption("SQL execution is intentionally unavailable in this frontend milestone.")
    with b:
        panel("Experiment detail", "Select a record after integration to inspect its complete source context, missing fields and uncertainty.")
        panel("Source provenance", "Original publication, printed page, data origin, rights and validation status will be shown beside each record.")

def compare():
    heading("Scientific context", "Compare & Analyze", "Set up careful comparisons that retain fuel, atmosphere, geometry and measurement-method context.")
    notice("Interface preview · No chart or numerical comparison is shown until the source-linked data service is connected.")
    a,b=st.columns(2,gap="large")
    with a: st.selectbox("First experiment",["Select a validated record in Phase 3"],disabled=True)
    with b: st.selectbox("Second experiment",["Select a validated record in Phase 3"],disabled=True)
    panel("Comparison table", "Shared conditions, differences, missing values and source references will be shown here.")
    panel("Chart area", "Charts will use validated numerical inputs and display original units and supporting sources.")
    panel("Scientific limitations", "Measurements from incompatible conditions will be flagged before interpretation.")

def lab():
    heading("Research to design", "Solution Lab", "Frame an engineering question and inspect relevant evidence before drawing design considerations.")
    notice("Interface preview · Evidence retrieval and engineering suggestions are not active in Phase 2.")
    st.text_area("Describe your research problem",placeholder="What fire-safety question are you investigating?",disabled=True)
    st.selectbox("Research context",["Choose conditions after evidence integration"],disabled=True)
    a,b=st.columns(2,gap="large")
    with a: panel("Supporting evidence", "Relevant experiments, source passages and applicability limits will appear here.")
    with b: panel("Engineering considerations", "Future suggestions will identify assumptions, unresolved questions and necessary validation.")
    panel("Limits and uncertainty", "This workspace will support research exploration. It will not certify spacecraft safety decisions.")

def assistant():
    heading("Evidence-grounded research", "AI Research Assistant", "Ask scientific questions with traceable source support once retrieval and citation checks are enabled.")
    notice("AI retrieval will be enabled in a later phase. No answer is generated in this preview.")
    panel("Conversation", "Research answers will distinguish direct observations from interpretation and show uncertainty alongside citations.")
    st.chat_input("Ask about microgravity combustion",disabled=True)
    a,b=st.columns(2,gap="large")
    with a: panel("Source citations", "Exact experiment and document references will be listed here.")
    with b: panel("Verification status", "Each scientific claim will require supporting evidence before display.")

def effect():
    heading("Visual research preview", "View Effect", "A place to examine documented flame behavior and the conditions behind it.")
    notice("Interface preview · This image is artwork, not experimental footage or a flame simulation.")
    st.image(str(ASSET),use_container_width=True)
    st.caption("Supplied Space Apps Challenge artwork. A separate flame-over-Earth asset was not supplied.")
    a,b=st.columns(2,gap="large")
    with a:
        st.selectbox("Research-backed preset",["Presets become available after source validation"],disabled=True)
        st.text_area("Scenario description",disabled=True,placeholder="Describe a documented experiment")
    with b:
        panel("Experimental conditions", "Fuel, atmosphere, gravity, airflow and apparatus will accompany each future visual.")
        panel("Evidence and limitations", "Authentic media, illustrations and model outputs will be labeled separately with sources and validation status.")

st.sidebar.image(str(ASSET),use_container_width=True)
st.sidebar.markdown("**FLAME IN FREEFALL**")
st.sidebar.caption("Research interface · Phase 2 preview")
pages=[st.Page(explorer,title="Research Explorer",icon="🔎",default=True),st.Page(records,title="Research Records",icon="📚"),st.Page(compare,title="Compare & Analyze",icon="📊"),st.Page(lab,title="Solution Lab",icon="🧪"),st.Page(assistant,title="AI Research Assistant",icon="💬"),st.Page(effect,title="View Effect",icon="🔥")]
st.navigation(pages,position="sidebar").run()