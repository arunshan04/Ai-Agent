import streamlit as st
from collections import Counter

def show_stats(tracks, hosts):
    """
    Displays the main statistics page with an overview of tracks and hosts.
    """
    st.header("Dashboard Overview")

    # --- Key Metrics ---
    st.markdown("### Key Metrics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Tracks", len(tracks) if tracks else 0)
    with col2:
        st.metric("Total Hosts", len(hosts) if hosts else 0)

    st.markdown("---")

    # --- Hosts by OS Type ---
    if hosts:
        st.markdown("### Hosts by Operating System")
        os_types = [h.get('os_type', 'Unknown') for h in hosts]
        os_counts = Counter(os_types)

        # Use columns for a better layout
        cols = st.columns(len(os_counts) or 1)
        i = 0
        for os_type, count in os_counts.items():
            # Cycle through columns if there are more OS types than columns
            with cols[i % len(cols)]:
                 st.markdown(f"""
                    <div class='stat-card'>
                        <div class='stat-title'>{os_type}</div>
                        <div class='stat-value'>{count}</div>
                    </div>
                """, unsafe_allow_html=True)
            i += 1

    st.markdown("---")

    # --- Tracks Overview ---
    if tracks:
        st.markdown("### Tracks Overview")
        unique_tracks = {t['name']: t for t in tracks}.values()

        for track in unique_tracks:
            track_name = track.get('name', 'Unnamed Track')
            track_desc = track.get('description', 'No description.')
            hosts_in_track = [h for h in hosts if h.get('track') == track.get('id')]
            with st.expander(f"**{track_name}** &mdash; {len(hosts_in_track)} hosts"):
                st.markdown(f"_{track_desc if track_desc else 'No description provided.'}_")
                if hosts_in_track:
                    for host in hosts_in_track:
                        st.markdown(f"- **{host.get('name')}** ({host.get('os_type')})")
                else:
                    st.write("No hosts are currently assigned to this track.")

    if not tracks and not hosts:
        st.info("No data available to display statistics. Please add tracks and hosts via the Django admin panel.")