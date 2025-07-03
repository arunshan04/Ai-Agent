import sqlite3
from typing import List, Optional
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

# It's good practice to allow CORS from your frontend's origin
# during development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # The origin of your React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = 'db.sqlite3'

# --- Pydantic Models for API responses ---

class Track(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

class Host(BaseModel):
    id: int
    name: str
    os_type: str
    track: int

class PackageVulnerability(BaseModel):
    cve_id: Optional[str] = None
    cve_title: Optional[str] = None
    cve_description: Optional[str] = None
    score: Optional[float] = None
    impact: Optional[str] = None
    status: Optional[str] = None
    updated_ts: Optional[datetime] = None

class TrackDetail(PackageVulnerability):
    host_id: int
    host_name: str
    os_type: str
    package_full_name: str

def dict_factory(cursor, row):
    """Converts database rows into dictionaries."""
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row)}

def get_db_conn():
    """FastAPI dependency to manage database connections."""
    # Use a URI for read-only mode and disable the thread check.
    db_uri = f"file:{DB_PATH}?mode=ro"
    conn = sqlite3.connect(db_uri, uri=True, check_same_thread=False)
    conn.row_factory = dict_factory
    try:
        yield conn
    finally:
        conn.close()

@app.get("/api/tracks/", response_model=List[Track])
def get_tracks(conn: sqlite3.Connection = Depends(get_db_conn)) -> List[Track]:
    """Fetches all unique tracks."""
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT id, name, description FROM cveapp_track")
    tracks = cursor.fetchall()
    return tracks

@app.get("/api/hosts/", response_model=List[Host])
def get_hosts(conn: sqlite3.Connection = Depends(get_db_conn)) -> List[Host]:
    """Fetches all hosts."""
    cursor = conn.cursor()
    # Alias track_id to track to match frontend expectations
    cursor.execute("SELECT id, name, os_type, track_id as track FROM cveapp_host")
    hosts = cursor.fetchall()
    return hosts

@app.get("/api/package-vulnerabilities/", response_model=List[PackageVulnerability])
def get_package_vulnerabilities(conn: sqlite3.Connection = Depends(get_db_conn)) -> List[PackageVulnerability]:
    """Fetches all package vulnerabilities."""
    cursor = conn.cursor()
    cursor.execute("SELECT cve_id, cve_title, cve_description, score, impact, status, updated_ts FROM package_vulnerabilities_mapping")
    vulns = cursor.fetchall()
    return vulns

@app.get("/api/track-detail/{track_id}/", response_model=List[TrackDetail])
def get_track_detail(track_id: int, conn: sqlite3.Connection = Depends(get_db_conn)) -> List[TrackDetail]:
    """Fetches all vulnerabilities for a given track, similar to the Streamlit app."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            h.id as host_id, h.name as host_name, h.os_type, hp.package_full_name,
            pvm.cve_id, pvm.cve_title, pvm.cve_description, pvm.score,
            pvm.impact, pvm.status, pvm.other_fields
        FROM cveapp_host h
        JOIN host_packages hp ON h.id = hp.host_id
        INNER JOIN package_vulnerabilities_mapping pvm ON hp.package_full_name = pvm.package_full_name
        WHERE h.track_id = ?
    """, (track_id,))
    results = cursor.fetchall()
    return results

@app.get("/api/cve-summary-charts/")
def get_cve_summary_charts(conn: sqlite3.Connection = Depends(get_db_conn)):
    cursor = conn.cursor()
    # CVEs by severity
    cursor.execute('SELECT severity, COUNT(*) FROM cve_summary GROUP BY severity')
    severity_data = {row['severity']: row['COUNT(*)'] for row in cursor.fetchall()}
    # CVEs by month (last 7 months)
    cursor.execute('SELECT substr(published_date, 1, 7) as month, COUNT(*) FROM cve_summary GROUP BY month ORDER BY month DESC LIMIT 7')
    month_data = cursor.fetchall()
    # CVEs by CVSS score (rounded)
    cursor.execute('SELECT ROUND(cvss_score), COUNT(*) FROM cve_summary GROUP BY ROUND(cvss_score) ORDER BY ROUND(cvss_score)')
    cvss_data = cursor.fetchall()
    return {
        'severity': severity_data,
        'monthly': [{'month': row['month'], 'count': row['COUNT(*)']} for row in month_data],
        'cvss': [{'score': row['ROUND(cvss_score)'] if row['ROUND(cvss_score)'] is not None else 'Unspecified', 'count': row['COUNT(*)']} for row in cvss_data],
    }