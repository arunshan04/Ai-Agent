
import streamlit as st
import requests

API_URL = "http://localhost:8000/api/"

# Custom CSS for colorful theme
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .main {
        background: transparent;
    }
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .css-1d391kg, .css-1v0mbdj, .css-1cpxqw2 { /* Card backgrounds */
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        padding: 1.5em 1em 1em 1em;
        margin-bottom: 1.5em;
    }
    .st-bb, .st-c3, .st-c6, .st-cg, .st-ch, .st-ci, .st-cj, .st-ck, .st-cl, .st-cm, .st-cn, .st-co, .st-cp, .st-cq, .st-cr, .st-cs, .st-ct, .st-cu, .st-cv, .st-cw, .st-cx, .st-cy, .st-cz {
        color: #333;
    }
    .stButton>button {
        background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1.5em;
        font-weight: bold;
        margin-top: 1em;
    }
    .stSelectbox>div>div {
        background: #fff;
        color: #333;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.set_page_config(page_title="CVE Dashboard", layout="wide")
st.markdown("<h1 style='color:#185a9d; font-weight:900;'>CVE Dashboard</h1>", unsafe_allow_html=True)

# Sidebar: OS selection
os_type = st.sidebar.selectbox("Select OS Type", ["windows", "linux"])

# Fetch hosts for selected OS
def get_hosts(os_type):
    resp = requests.get(f"{API_URL}hosts/", params={})
    if resp.status_code == 200:
        return [h for h in resp.json() if h["os_type"] == os_type]
    return []

hosts = get_hosts(os_type)
host_names = [h["name"] for h in hosts]

selected_host = st.sidebar.selectbox("Select Host", host_names) if host_names else None

# Fetch CVEs for selected host
def get_cves_for_host(host_id):
    resp = requests.get(f"{API_URL}hostcves/by_host/", params={"host_id": host_id})
    if resp.status_code == 200:
        return resp.json()
    return []

if selected_host:
    host_id = next(h["id"] for h in hosts if h["name"] == selected_host)
    host_cves = get_cves_for_host(host_id)
    st.markdown(f"<h2 style='color:#764ba2;'>CVEs for {selected_host} ({os_type})</h2>", unsafe_allow_html=True)
    cols = st.columns(2)
    card_colors = ["#ffecd2", "#fcb69f", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#a6c1ee"]
    for idx, hc in enumerate(host_cves):
        cve = hc["cve"]
        with cols[idx % 2]:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {card_colors[idx%len(card_colors)]} 0%, #fff 100%); border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); padding: 1.5em 1em 1em 1em; margin-bottom: 1.5em;'>
                    <h3 style='color:#185a9d;'>{cve['cve_id']}</h3>
                    <p><b>Description:</b> {cve['description']}</p>
                    <p><b>Score:</b> <span style='color:#e17055;font-weight:bold;'>{cve['score']}</span></p>
                    <p><b>Impact:</b> <span style='color:#00b894;'>{cve['impact']}</span></p>
                </div>
            """, unsafe_allow_html=True)
else:
    st.info("No hosts available for the selected OS.")
