import React, { useEffect, useState } from 'react';
import axios from 'axios';

const TrackView = ({ selectedTrack, tracks }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        const trackObj = tracks.find(t => t.name === selectedTrack);
        if (!trackObj) {
          setResults([]);
          setLoading(false);
          return;
        }
        const res = await axios.get(`/api/track-detail/${trackObj.id}/`);
        setResults(res.data);
      } catch (err) {
        setError('Could not fetch data for this track.');
      }
      setLoading(false);
    };
    if (selectedTrack && tracks.length) fetchData();
  }, [selectedTrack, tracks]);

  if (!selectedTrack) return <div>No track selected.</div>;
  if (loading) return <div>Loading...</div>;
  if (error) return <div style={{ color: 'red' }}>{error}</div>;

  return (
    <div>
      <h3>Hosts and Package Vulnerabilities for Track: {selectedTrack}</h3>
      {results.length ? results.map((row, idx) => (
        <div key={idx} style={{ border: '1px solid #eee', borderRadius: 8, margin: '1em 0', padding: 16 }}>
          <b>Host:</b> {row.host_name} ({row.os_type})<br />
          <b>Package:</b> {row.package_name}<br />
          <b>CVE ID:</b> {row.cve_id || <span style={{ color: '#888' }}>None</span>}<br />
          <b>Title:</b> {row.cve_title || <span style={{ color: '#888' }}>None</span>}<br />
          <b>Description:</b> {row.cve_description || <span style={{ color: '#888' }}>None</span>}<br />
          <b>Score:</b> <span>{row.score || '-'}</span><br />
          <b>Impact:</b> <span>{row.impact || '-'}</span><br />
          <b>Status:</b> {row.status || '-'}<br />
          <b>Other:</b> {row.other_fields || '-'}
        </div>
      )) : <div>No hosts/packages/vulnerabilities found for this track.</div>}
    </div>
  );
};

export default TrackView;
