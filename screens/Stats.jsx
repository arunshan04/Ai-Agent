import React from 'react';

const Stats = ({ tracks, hosts }) => {
  // Count OS types
  const osCounts = hosts ? hosts.reduce((acc, h) => {
    const os = h.os_type || 'Unknown';
    acc[os] = (acc[os] || 0) + 1;
    return acc;
  }, {}) : {};

  return (
    <div>
      <h2>Dashboard Overview</h2>
      <h3>Key Metrics</h3>
      <div style={{ display: 'flex', gap: '2rem' }}>
        <div>
          <strong>Total Tracks:</strong> {tracks ? tracks.length : 0}
        </div>
        <div>
          <strong>Total Hosts:</strong> {hosts ? hosts.length : 0}
        </div>
      </div>
      <hr />
      {hosts && (
        <div>
          <h3>Hosts by Operating System</h3>
          <div style={{ display: 'flex', gap: '1rem' }}>
            {Object.entries(osCounts).map(([os, count]) => (
              <div key={os} style={{ border: '1px solid #ccc', borderRadius: 8, padding: 12, minWidth: 120 }}>
                <div style={{ fontWeight: 'bold' }}>{os}</div>
                <div style={{ fontSize: 24 }}>{count}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      <hr />
    </div>
  );
};

export default Stats;
