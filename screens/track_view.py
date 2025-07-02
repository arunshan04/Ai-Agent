import streamlit as st
import sqlite3

def show_track_view(selected_track, tracks):
    track_id = next((t["id"] for t in tracks if t["name"] == selected_track), None)
    if not track_id:
        st.info("No track selected or track not found.")
        return
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.id, h.name, h.os_type, hp.package_name, pvm.cve_id, pvm.cve_title, pvm.cve_description, pvm.score, pvm.impact, pvm.status, pvm.other_fields
        FROM cveapp_host h
        JOIN host_packages hp ON h.id = hp.host_id
        INNER JOIN package_vulnerabilities_mapping pvm ON hp.package_name = pvm.package_name
        WHERE h.track_id = ?
    """, (track_id,))
    results = cursor.fetchall()
    conn.close()
    st.subheader(f"Hosts and Package Vulnerabilities for Track: {selected_track}")
    if results:
        for row in results:
            host_id, host_name, os_type, package_name, cve_id, cve_title, cve_description, score, impact, status, other_fields = row
            st.markdown(f"""
                <div class='host-vuln-card'>
                    <b>Host:</b> {host_name} ({os_type})<br>
                    <b>Package:</b> {package_name}<br>
                    <b>CVE ID:</b> {cve_id or "<span class='none'>None</span>"}<br>
                    <b>Title:</b> {cve_title or "<span class='none'>None</span>"}<br>
                    <b>Description:</b> {cve_description or "<span class='none'>None</span>"}<br>
                    <b>Score:</b> <span class='vuln-score'>{score or '-'}</span><br>
                    <b>Impact:</b> <span class='vuln-impact'>{impact or '-'}</span><br>
                    <b>Status:</b> {status or '-'}<br>
                    <b>Other:</b> {other_fields or '-'}
                </div>
""", unsafe_allow_html=True)
    else:
        st.info("No hosts/packages/vulnerabilities found for this track.")
