import streamlit as st
import requests
from screens.vulnerabilities import show_vulnerabilities
from screens.track_view import show_track_view

API_URL = "http://localhost:8000/api/"

# Load external CSS (robust for both local and Streamlit Cloud)
import os
css_path = os.path.join(os.path.dirname(__file__), "assets", "dashboard.css")
with open(css_path) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.set_page_config(page_title="CVE Dashboard", layout="wide")
st.markdown("<h1 style='color:#185a9d; font-weight:900;'>CVE Dashboard</h1>", unsafe_allow_html=True)

# Sidebar state and data
if 'sidebar_menu' not in st.session_state:
    st.session_state['sidebar_menu'] = 'Tracks'
tracks_resp = requests.get(f"{API_URL}tracks/")
tracks = tracks_resp.json() if tracks_resp.status_code == 200 else []
if 'sidebar_tracks_open' not in st.session_state:
    st.session_state['sidebar_tracks_open'] = False




# Sidebar (simple version)
with st.sidebar:
    if st.button("Tracks", key="toggle_tracks_sidebar"):
        st.session_state['sidebar_tracks_open'] = not st.session_state['sidebar_tracks_open']
    if st.session_state['sidebar_tracks_open']:
        seen = set()
        for t in tracks:
            if t['name'] in seen:
                continue
            seen.add(t['name'])
            if st.button(t['name'], key=f"track_{t['id']}_sidebar"):
                st.session_state['sidebar_menu'] = 'Tracks'
                st.session_state['selected_track'] = t['name']
    if st.button("Vulnerabilities", key="menu_Vulnerabilities_sidebar"):
        st.session_state['sidebar_menu'] = 'Vulnerabilities'
        st.session_state['sidebar_tracks_open'] = False

sidebar_tag = st.session_state['sidebar_menu']
if sidebar_tag == "Tracks":
    selected_track = st.session_state.get('selected_track')
    if selected_track:
        show_track_view(selected_track, tracks)
    else:
        st.info("Select a track to view hosts and package vulnerabilities.")
elif sidebar_tag == "Vulnerabilities":
    show_vulnerabilities()
