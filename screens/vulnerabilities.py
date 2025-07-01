import streamlit as st
import requests

def show_vulnerabilities(api_url):
    try:
        response = requests.get(f"{api_url}package-vulnerabilities/")
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        vulns = response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Could not fetch vulnerabilities from API: {e}")
        return

    st.subheader("All Package Vulnerabilities in the System")

    if not vulns:
        st.info("No vulnerabilities found in the system.")
        return

    cols = st.columns(2)
    card_colors = ["#ffecd2", "#fcb69f", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#a6c1ee"]
    for idx, v in enumerate(vulns):
        # Access data by key from the dictionary
        cve_id = v.get('cve_id', 'N/A')
        cve_title = v.get('cve_title', 'N/A')
        updated_ts = v.get('updated_ts', '')
        with cols[idx % 2]:
            st.markdown(f"""
                <div class='vuln-card'>
                    <div style='display:flex;justify-content:space-between;align-items:center;'>
                        <span class='vuln-title' style='color:#7c5cd6;font-weight:bold;font-size:1.1em;'>
                            <a href='#' style='color:#7c5cd6;text-decoration:none;'>{cve_id}</a>
                        </span>
                        <span style='color:#888;font-size:1em;'><i class='fa fa-clock-o'></i> {updated_ts[11:16] if updated_ts else ''}</span>
                    </div>
                    <div style='border-top:1px solid #eee;padding-top:0.5em;margin-top:0.3em;'>
                        <div style='font-size:1.08em;margin-bottom:0.5em;'>{v.get('cve_title', 'No Title')}</div>
                        <p><b>Description:</b> {v.get('cve_description', 'N/A')}</p>
                        <p><b>Score:</b> <span class='vuln-score'>{v.get('score', '-')}</span></p>
                        <p><b>Impact:</b> <span class='vuln-impact'>{v.get('impact', '-')}</span></p>
                        <p><b>Status:</b> {v.get('status', '-')}</p>
                        <p><b>Other:</b> {v.get('other_fields', '-')}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
