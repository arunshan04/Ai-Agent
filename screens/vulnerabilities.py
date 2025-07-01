import streamlit as st
import sqlite3

def show_vulnerabilities():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT package_name, cve_id, cve_title, cve_description, score, impact, status, other_fields, updated_ts FROM package_vulnerabilities_mapping")
    vulns = cursor.fetchall()
    conn.close()
    st.subheader("All Package Vulnerabilities in the System")
    cols = st.columns(2)
    card_colors = ["#ffecd2", "#fcb69f", "#a1c4fd", "#c2e9fb", "#fbc2eb", "#a6c1ee"]
    for idx, v in enumerate(vulns):
        package_name, cve_id, cve_title, cve_description, score, impact, status, other_fields, updated_ts = v
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
                        <div style='font-size:1.08em;margin-bottom:0.5em;'>{cve_title}</div>
                        <p><b>Description:</b> {cve_description}</p>
                        <p><b>Score:</b> <span class='vuln-score'>{score}</span></p>
                        <p><b>Impact:</b> <span class='vuln-impact'>{impact}</span></p>
                        <p><b>Status:</b> {status}</p>
                        <p><b>Other:</b> {other_fields}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
