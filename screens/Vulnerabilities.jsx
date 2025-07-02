import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Vulnerabilities = () => {
  const [vulns, setVulns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchVulns = async () => {
      setLoading(true);
      setError(null);
      try {
        const res = await axios.get('/api/package-vulnerabilities/');
        setVulns(res.data);
      } catch (err) {
        setError('Could not fetch vulnerabilities from API.');
      }
      setLoading(false);
    };
    fetchVulns();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h3>All Package Vulnerabilities in the System</h3>
      {!vulns.length ? <div>No vulnerabilities found in the system.</div> : (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1em' }}>
          {vulns.map((v, idx) => (
            <div key={idx} style={{ background: '#f7f7fa', border: '1px solid #eee', borderRadius: 8, padding: 16, minWidth: 300 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#7c5cd6', fontWeight: 'bold', fontSize: '1.1em' }}>{v.cve_id}</span>
                <span style={{ color: '#888', fontSize: '1em' }}>{v.updated_ts ? v.updated_ts.slice(11, 16) : ''}</span>
              </div>
              <div style={{ borderTop: '1px solid #eee', paddingTop: '0.5em', marginTop: '0.3em' }}>
                <div style={{ fontSize: '1.08em', marginBottom: '0.5em' }}>{v.cve_title || 'No Title'}</div>
                <p><b>Description:</b> {v.cve_description || 'N/A'}</p>
                <p><b>Score:</b> <span>{v.score || '-'}</span></p>
                <p><b>Impact:</b> <span>{v.impact || '-'}</span></p>
                <p><b>Status:</b> {v.status || '-'}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Vulnerabilities;
