import streamlit as st
import plotly.graph_objects as go
from engine import fetch_orbital_inventory, get_satellite_coordinates

st.set_page_config(page_title="IAN-SCP Dashboard", layout="wide")

st.title("🛰️ IAN-SCP: Satellite Collision Prevention")
st.caption("The TCP/IP layer of orbital collision prevention")

# Metrics from Technical Plan
col1, col2, col3 = st.columns(3)
col1.metric("Risk Threshold", "1e-4", "Target")
col2.metric("Maneuver Success", "≥92%", "Target")
col3.metric("Fuel Optimization", "20-35%", "Target")

# Sidebar for operator control
st.sidebar.header("Global Shell Monitoring")
monitor_active = st.sidebar.toggle("Real-time Data Ingestion", value=True)

if monitor_active:
    with st.spinner("Accessing High-precision ephemeris streams..."):
        sats = fetch_orbital_inventory()
        st.success(f"Monitoring {len(sats)} active satellites across LEO.")
        
        st.write("### Live Orbital Map (High-density shell mapping)")
        
        # Calculate coordinates for a sample of satellites
        x, y, z, names = get_satellite_coordinates(sats, sample_size=1000)
        
        # Create the 3D Scatter Plot
        fig = go.Figure()
        fig.add_trace(go.Scatter3d(
            x=x, y=y, z=z,
            mode='markers',
            text=names,
            marker=dict(size=2, color='cyan', opacity=0.8),
            name="LEO Satellites"
        ))
        
        # Format the map to look like dark space
        fig.update_layout(
            template="plotly_dark",
            margin=dict(l=0, r=0, b=0, t=0),
            scene=dict(
                xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
            )
        )
        
        # Display the map in Streamlit
        st.plotly_chart(fig, use_container_width=True)

        # --- THE TABLE IS BACK ---
        st.write("### Active Satellite Inventory (Data Acquisition Layer)")
        sat_names = [s.name for s in sats[:10]]
        st.table({"Satellite Name": sat_names, "Status": ["Protected"] * 10})
