
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



st.markdown(
    '''
    <style>
    .sidebar-menu {
        list-style: none;
        padding: 0;
        margin: 0 0 2em 0;
    }
    .sidebar-menu li {
        margin-bottom: 0.5em;
    }
    .sidebar-menu li a {
        display: flex;
        align-items: center;
        text-decoration: none;
        color: #fff;
        background: #764ba2;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: bold;
        transition: background 0.2s;
    }
    .sidebar-menu li.active a, .sidebar-menu li a:hover {
        background: #43cea2;
        color: #222;
    }
    .sidebar-menu li i {
        margin-right: 0.7em;
    }
    </style>
    ''', unsafe_allow_html=True)


# Sidebar menu with treeview for Tracks
if 'sidebar_menu' not in st.session_state:
    st.session_state['sidebar_menu'] = 'Tracks'
if 'sidebar_tracks_open' not in st.session_state:
    st.session_state['sidebar_tracks_open'] = False

tracks_resp = requests.get(f"{API_URL}tracks/")
tracks = tracks_resp.json() if tracks_resp.status_code == 200 else []

st.sidebar.markdown('<ul class="sidebar-menu">', unsafe_allow_html=True)





# Custom sidebar dropdown for Tracks (styled like sample image)
sidebar_css = '''
<style>
.custom-sidebar {
  background: #231942;
  color: #fff;
  padding: 0;
  border-radius: 0 20px 20px 0;
  min-width: 220px;
}
.custom-sidebar ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.custom-sidebar li {
  margin: 0;
  padding: 0;
}
.custom-sidebar .sidebar-header {
  font-size: 1.1em;
  font-weight: bold;
  padding: 1.2em 1.2em 0.5em 1.2em;
  color: #fff;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
}
.custom-sidebar .sidebar-link {
  display: flex;
  align-items: center;
  padding: 0.9em 1.2em;
  color: #bcbcbc;
  text-decoration: none;
  font-size: 1.08em;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  transition: background 0.2s, color 0.2s;
  border-radius: 8px;
  margin-bottom: 2px;
}
.custom-sidebar .sidebar-link.selected, .custom-sidebar .sidebar-link:hover {
  background: #3a2676;
  color: #fff;
}
.custom-sidebar .sidebar-dropdown {
  background: none;
  border: none;
  color: #fff;
  font-size: 1.08em;
  font-weight: 600;
  width: 100%;
  text-align: left;
  padding: 0.9em 1.2em;
  display: flex;
  align-items: center;
  cursor: pointer;
  border-radius: 8px;
  margin-bottom: 2px;
}
.custom-sidebar .dropdown-arrow {
  margin-left: auto;
  font-size: 1.2em;
  transition: transform 0.2s;
}
.custom-sidebar .dropdown-arrow.open {
  transform: rotate(180deg);
}
.custom-sidebar .sidebar-sublist {
  padding-left: 1.8em;
  background: #2d2156;
  border-radius: 0 0 8px 8px;
}
.custom-sidebar .sidebar-subitem {
  margin-bottom: 0.2em;
}
.custom-sidebar .sidebar-subitem .sidebar-link {
  font-size: 1em;
  color: #bcbcbc;
  background: none;
}
.custom-sidebar .sidebar-subitem .sidebar-link.selected, .custom-sidebar .sidebar-subitem .sidebar-link:hover {
  color: #fff;
  background: #3a2676;
}
</style>
'''
st.markdown(sidebar_css, unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="custom-sidebar">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-header"><span style="margin-right:0.5em;">�️</span>Tracks <span class="dropdown-arrow{}">&#9660;</span></div>'.format(' open' if st.session_state['sidebar_tracks_open'] else ''), unsafe_allow_html=True)
    if st.button("Tracks", key="dropdown_tracks", help="Expand/collapse tracks", use_container_width=True):
        st.session_state['sidebar_tracks_open'] = not st.session_state['sidebar_tracks_open']
    if st.session_state['sidebar_tracks_open']:
        st.markdown('<ul class="sidebar-sublist" style="margin-top:0;">', unsafe_allow_html=True)
        seen = set()
        for t in tracks:
            if t['name'] in seen:
                continue  # Skip duplicate track names
            seen.add(t['name'])
            # Only show IIP once, and only as a disabled button
            if t['name'] == 'IIP':
                st.markdown(f'<li class="sidebar-subitem"><button class="sidebar-link" disabled>{t["name"]}</button></li>', unsafe_allow_html=True)
                break
            btn_class = "sidebar-link selected" if st.session_state.get('selected_track') == t['name'] else "sidebar-link"
            if st.button(t['name'], key=f"track_{t['id']}", help=t['name'], args=None):
                st.session_state['sidebar_menu'] = 'Tracks'
                st.session_state['selected_track'] = t['name']
                st.session_state['sidebar_tracks_open'] = True
            st.markdown(f'<li class="sidebar-subitem"><button class="{btn_class}" disabled>{t["name"]}</button></li>', unsafe_allow_html=True)
        st.markdown('</ul>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)





# Vulnerabilities menu (no expander/dropdown, just button)
vuln_btn_style = "background: linear-gradient(90deg, #43cea2 0%, #185a9d 100%); color: white; border: none; border-radius: 12px; padding: 0.7em 2em; font-weight: bold; font-size: 1.2em; margin-bottom: 1em; min-width: 120px; min-height: 48px;"
if st.sidebar.button("Vulnerabilities", key="menu_Vulnerabilities"):
    st.session_state['sidebar_menu'] = 'Vulnerabilities'
    st.session_state['sidebar_tracks_open'] = False

# JS to toggle treeview (Streamlit workaround: reload page)
import streamlit.components.v1 as components
components.html('''<script>
window.addEventListener('message', (event) => {
    if (event.data && event.data.type === 'toggleTracksTree') {
        window.location.reload();
    }
});
</script>''', height=0)

sidebar_tag = st.session_state['sidebar_menu']


if sidebar_tag == "Tracks":
    selected_track = st.session_state.get('selected_track')
    hosts = []
    if selected_track:
        track_id = next((t["id"] for t in tracks if t["name"] == selected_track), None)
        hosts_resp = requests.get(f"{API_URL}hosts/?track={track_id}")
        if hosts_resp.status_code == 200:
            hosts = hosts_resp.json()
    # Fetch CVEs for all hosts in the selected track
    track_cves = []
    if selected_track and hosts:
        host_ids = [h["id"] for h in hosts]
        for host_id in host_ids:
            cves_resp = requests.get(f"{API_URL}hostcves/by_host/", params={"host_id": host_id})
            if cves_resp.status_code == 200:
                track_cves.extend(cves_resp.json())

    if selected_track:
        st.subheader(f"CVEs for Track: {selected_track}")
        cols = st.columns(2)
        card_colors = ["#ffecd2", "#fcb69f", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#a6c1ee"]
        for idx, hc in enumerate(track_cves):
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
        st.info("No tracks or hosts available.")

elif sidebar_tag == "Vulnerabilities":
    cves_resp = requests.get(f"{API_URL}cves/")
    cves = cves_resp.json() if cves_resp.status_code == 200 else []
    st.subheader("All Vulnerabilities in the System")
    cols = st.columns(2)
    card_colors = ["#ffecd2", "#fcb69f", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#a6c1ee"]
    for idx, cve in enumerate(cves):
        with cols[idx % 2]:
            st.markdown(f"""
                <div style='background: linear-gradient(135deg, {card_colors[idx%len(card_colors)]} 0%, #fff 100%); border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,0.08); padding: 1.5em 1em 1em 1em; margin-bottom: 1.5em;'>
                    <h3 style='color:#185a9d;'>{cve['cve_id']}</h3>
                    <p><b>Description:</b> {cve['description']}</p>
                    <p><b>Score:</b> <span style='color:#e17055;font-weight:bold;'>{cve['score']}</span></p>
                    <p><b>Impact:</b> <span style='color:#00b894;'>{cve['impact']}</span></p>
                </div>
            """, unsafe_allow_html=True)
