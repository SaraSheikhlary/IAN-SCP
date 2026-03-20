import streamlit as st
import plotly.graph_objects as go
import time
from engine import (
    fetch_orbital_inventory, 
    get_satellite_coordinates, 
    detect_high_risk_conjunctions, 
    calculate_evasion_maneuver
)

# 1. PAGE CONFIG (Must be absolutely first)
st.set_page_config(page_title="AstroShield AI", page_icon="🛰️", layout="wide")

# 2. FORCE DARK THEME & GALAXY BACKGROUND
def apply_force_theme():
    st.markdown(
        """
        <style>
        /* Force background on the main container and the root */
        [data-testid="stAppViewContainer"], .main, .stApp {
            background-image: url("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=2072&auto=format&fit=crop") !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            background-position: center !important;
        }

        /* Clean up the header area so it's transparent */
        [data-testid="stHeader"] {
            background: rgba(0,0,0,0) !important;
            color: white !important;
        }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: rgba(10, 10, 20, 0.95) !important;
        }

        /* Force ALL text to white and add glow to headers */
        h1, h2, h3, p, span, label, .stMetric label {
            color: #ffffff !important;
        }
        
        h1, h2, h3 {
            text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.6) !important;
            color: #00d4ff !important;
        }

        /* NEW: Force Title (h1) to stay on one line */
        h1 {
            font-size: 2.2rem !important;
            white-space: nowrap !important;
        }

        /* Glassmorphism for Metrics and Cards */
        [data-testid="stMetric"], [data-testid="stVerticalBlock"] > div, .stTabs {
            background: rgba(14, 17, 23, 0.8) !important;
            backdrop-filter: blur(12px) !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 15px !important;
            padding: 20px !important;
        }
        
        /* Ensure the Plotly chart background is transparent */
        .js-plotly-plot .plotly .main-svg {
            background: transparent !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

apply_force_theme()

# --- The ORIGINAL LOGIC (Unchanged) ---
st.title("🛰️ AstroShield AI: Satellite Collision Prevention")

col1, col2, col3 = st.columns(3)
col1.metric("Risk Threshold", "1e-4", "Target")
col2.metric("Maneuver Success", "≥92%", "Target")
col3.metric("Fuel Optimization", "20-35%", "Target")

st.sidebar.header("Global Shell Monitoring")
monitor_active = st.sidebar.toggle("Real-time Data Ingestion", value=True)

if monitor_active:
    with st.spinner("Accessing High-precision ephemeris streams..."):
        sats = fetch_orbital_inventory()
        st.success(f"Monitoring {len(sats)} active satellites across LEO.")

        tab1, tab2, tab3 = st.tabs(["🌐 3D Orbital Map", "📋 Active Inventory", "⚠️ Risk Engine Alerts"])
        
        with tab1:
            st.write("### Live Orbital Map (High-density shell mapping)")
            x, y, z, names = get_satellite_coordinates(sats, sample_size=1000)

            fig = go.Figure()
            fig.add_trace(go.Scatter3d(
                x=x, y=y, z=z,
                mode='markers',
                text=names,
                marker=dict(size=2, color='cyan', opacity=0.8),
                name="LEO Satellites"
            ))

            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=0),
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                scene=dict(
                    xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                ),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.write("### Data Acquisition Layer")
            st.caption("Real-time list of ingested satellite telemetry.")

            # --- NEW: Live Search Bar ---
            search_term = st.text_input("🔍 Search Active Inventory (e.g., STARLINK, ISS, NOAA)", "STARLINK")
            
            # Filter the satellite list based on what the user types
            filtered_names = [s.name for s in sats if search_term.upper() in s.name.upper()]
            
            # Grab up to 50 results so the browser doesn't slow down
            display_names = filtered_names[:50]
            
            # Display the table dynamically
            if len(display_names) > 0:
                st.table({
                    "Satellite Name": display_names, 
                    "Operator/Type": ["SpaceX" if "STARLINK" in name else "Tracked Asset" for name in display_names],
                    "Status": ["Protected"] * len(display_names)
                })
            else:
                st.warning(f"No active satellites found matching '{search_term}'.")

        with tab3:
            st.write("### Autonomous Risk Prediction Engine")
            with st.spinner("Calculating orbital conjunctions..."):
                alerts = detect_high_risk_conjunctions(x, y, z, names)
                if len(alerts) > 0:
                    st.error(f"CRITICAL: {len(alerts)} high-risk conjunctions detected!")
                    st.table(alerts)
                    st.divider()
                    if st.button("Calculate Optimal Maneuvers"):
                        solutions = calculate_evasion_maneuver(alerts)
                        st.table(solutions)
                        if st.button("🚀 Authorize & Uplink Maneuvers", type="primary"):
                            st.balloons()
                else:
                    st.success("Clear: No high-risk conjunctions detected.")

# --- FOOTER ---
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: rgba(255, 255, 255, 0.6); font-size: 0.85em; padding-bottom: 20px;'>
        © 2026 AstroShield AI. All rights reserved.<br>
        <i>Powered by high-precision ephemeris streams and autonomous risk prediction.</i>
    </div>
    """, 
    unsafe_allow_html=True
)
