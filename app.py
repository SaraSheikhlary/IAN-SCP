import streamlit as st
import plotly.graph_objects as go
import numpy as np  # <-- NEW: Needed for Earth math
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

# --- The ORIGINAL LOGIC ---
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
            
            x, y, z, names = get_satellite_coordinates(sats)

            x_act, y_act, z_act, names_act = [], [], [], []
            x_deb, y_deb, z_deb, names_deb = [], [], [], []

            for i in range(len(names)):
                if 'DEB' in str(names[i]).upper():
                    x_deb.append(x[i])
                    y_deb.append(y[i])
                    z_deb.append(z[i])
                    names_deb.append(names[i])
                else:
                    x_act.append(x[i])
                    y_act.append(y[i])
                    z_act.append(z[i])
                    names_act.append(names[i])

            fig = go.Figure()

            # --- NEW: HOLOGRAPHIC EARTH LAYER ---
            # Earth's radius is roughly 6371 km
            R = 6371 
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 100)
            x_surf = R * np.outer(np.cos(u), np.sin(v))
            y_surf = R * np.outer(np.sin(u), np.sin(v))
            z_surf = R * np.outer(np.ones(np.size(u)), np.cos(v))

            fig.add_trace(go.Surface(
                x=x_surf, y=y_surf, z=z_surf,
                colorscale=[[0, '#020617'], [1, '#0ea5e9']], # Cyberpunk Dark Blue to Cyan
                showscale=False,
                opacity=0.5, # Slightly transparent so you can see orbits behind it!
                hoverinfo='skip',
                name="Earth"
            ))
            
            # Layer 1: Active Satellites (Cyan/Blue)
            fig.add_trace(go.Scatter3d(
                x=x_act, y=y_act, z=z_act,
                mode='markers', text=names_act, hoverinfo='text',
                marker=dict(size=2, color='#00f2fe', opacity=0.6), 
                name="Active Assets"
            ))
            
            # Layer 2: Debris (Bright Red)
            fig.add_trace(go.Scatter3d(
                x=x_deb, y=y_deb, z=z_deb,
                mode='markers', text=names_deb, hoverinfo='text',
                marker=dict(size=3, color='#ff003c', opacity=1.0), 
                name="Lethal Debris"
            ))

            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=0),
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
                scene=dict(
                    xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)) # Zooms the camera out perfectly
                ),
                height=600
            )
            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            st.write("### Data Acquisition Layer")
            st.caption("Real-time list of ingested satellite telemetry.")

            search_term = st.text_input("🔍 Search Active Inventory (e.g., STARLINK, ISS, DEB)", "STARLINK")
            filtered_names = [s.name for s in sats if search_term.upper() in s.name.upper()]
            display_names = filtered_names[:50]
            
            if len(display_names) > 0:
                st.table({
                    "Asset Name": display_names, 
                    "Classification": ["Debris" if "DEB" in name else ("SpaceX" if "STARLINK" in name else "Tracked Asset") for name in display_names],
                    "Status": ["Lethal Threat" if "DEB" in name else "Protected" for name in display_names]
                })
            else:
                st.warning(f"No objects found matching '{search_term}'.")

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
