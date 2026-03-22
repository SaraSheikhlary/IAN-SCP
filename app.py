import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
from engine import (
    fetch_orbital_inventory,
    get_satellite_coordinates,
    detect_high_risk_conjunctions,
    calculate_evasion_maneuver
)

# --- PUBLIC ACCESS LINKS ---
ASTROSHIELD_FAVICON_URL = "https://raw.githubusercontent.com/SaraSheikhlary/AstroShield-AI/main/Astroshield_favicon_square.png"
ASTROSHIELD_SIDEBAR_LOGO_URL = "https://raw.githubusercontent.com/SaraSheikhlary/AstroShield-AI/main/Astroshield_logo_wide.png"

# 1. PAGE CONFIG (Must be the very first Streamlit command)
st.set_page_config(
    page_title="AstroShield AI | Satellite Collision Avoidance Digital Twin",
    page_icon=ASTROSHIELD_FAVICON_URL,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://astroshield-ai.com',
        'Report a bug': 'https://github.com/SaraSheikhary/astroshield',
        'About': 'AstroShield AI: Real-time SGP4 orbital tracking and risk mitigation engine.'
    }
)

# --- INITIALIZE SESSION STATE FOR ROUTING ---
if 'entered_app' not in st.session_state:
    st.session_state.entered_app = False

# ==========================================
#         SCREEN 1: LANDING PAGE
# ==========================================
if not st.session_state.entered_app:
    # Cinematic Earth Background for the landing page
    st.markdown(
        """
        <style>
        [data-testid="stAppViewContainer"], .main, .stApp {
            background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop") !important;
            background-attachment: fixed !important;
            background-size: cover !important;
            background-position: center !important;
        }
        [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: white !important; }
        [data-testid="stSidebar"] { display: none !important; } /* Hide sidebar on landing page */
        </style>
        """,
        unsafe_allow_html=True
    )
    
    # Vertically push content down to center it
    st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Centered Logo
        st.image(ASTROSHIELD_SIDEBAR_LOGO_URL, use_container_width=True)
        st.markdown("<h3 style='text-align: center; color: white; text-shadow: 0px 0px 10px #00d4ff;'>Planetary Defense & Orbital Intelligence</h3><br>", unsafe_allow_html=True)
        
        # Big Enter Button
        if st.button("🚀 INITIATE SYSTEM", use_container_width=True, type="primary"):
            st.session_state.entered_app = True
            st.rerun() # Immediately reloads the script to show the main app

# ==========================================
#         SCREEN 2: MAIN DASHBOARD
# ==========================================
else:
    # FORCE DARK THEME & GALAXY BACKGROUND 
    def apply_force_theme():
        st.markdown(
            """
            <style>
            [data-testid="stAppViewContainer"], .main, .stApp {
                background-image: url("https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=2072&auto=format&fit=crop") !important;
                background-attachment: fixed !important;
                background-size: cover !important;
                background-position: center !important;
            }
            [data-testid="stHeader"] { background: rgba(0,0,0,0) !important; color: white !important; }
            [data-testid="stSidebar"] { background-color: rgba(10, 10, 20, 0.95) !important; }
            h1, h2, h3, p, span, label, .stMetric label { color: #ffffff !important; }
            h1, h2, h3 { text-shadow: 0px 0px 15px rgba(0, 212, 255, 0.6) !important; color: #00d4ff !important; }
            h1 { font-size: 2.2rem !important; white-space: nowrap !important; }
            [data-testid="stMetric"], [data-testid="stVerticalBlock"] > div, .stTabs {
                background: rgba(14, 17, 23, 0.8) !important;
                backdrop-filter: blur(12px) !important;
                border: 1px solid rgba(255, 255, 255, 0.1) !important;
                border-radius: 15px !important;
                padding: 20px !important;
            }
            .js-plotly-plot .plotly .main-svg { background: transparent !important; }
            </style>
            """,
            unsafe_allow_html=True
        )

    apply_force_theme()

    # --- MAIN UI ---
    st.title("🛰️ AstroShield AI: Satellite Collision Prevention")

    col1, col2, col3 = st.columns(3)
    col1.metric("Risk Threshold", "1e-4", "Target")
    col2.metric("Maneuver Success", "≥92%", "Target")
    col3.metric("Fuel Optimization", "20-35%", "Target")

    # --- SIDEBAR ---
    st.sidebar.image(ASTROSHIELD_SIDEBAR_LOGO_URL, use_container_width=True)
    st.sidebar.markdown("<br>", unsafe_allow_html=True) 

    st.sidebar.header("Global Shell Monitoring")
    monitor_active = st.sidebar.toggle("Real-time Data Ingestion", value=True)

    if monitor_active:
        with st.spinner("Accessing High-precision ephemeris streams..."):
            sats = fetch_orbital_inventory()
            st.success(f"Monitoring {len(sats)} tracked objects across LEO.")

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

                # --- PROFESSIONAL HOLOGRAPHIC WIREFRAME EARTH ---
                R = 6371  # Earth radius in km
                u = np.linspace(0, 2 * np.pi, 60)
                v = np.linspace(0, np.pi, 60)

                # 1. Dark Translucent Core
                x_surf = R * np.outer(np.cos(u), np.sin(v))
                y_surf = R * np.outer(np.sin(u), np.sin(v))
                z_surf = R * np.outer(np.ones(np.size(u)), np.cos(v))

                fig.add_trace(go.Surface(
                    x=x_surf, y=y_surf, z=z_surf,
                    colorscale=[[0, '#020617'], [1, '#052e47']],  # Deep space blue
                    showscale=False, opacity=0.8, hoverinfo='skip', name="Earth Core"
                ))

                # 2. Glowing Latitude/Longitude Graticules
                line_color = '#00d4ff'

                # Latitudes
                for lat in np.linspace(-np.pi / 2 + 0.2, np.pi / 2 - 0.2, 8):
                    x_lat = R * 1.02 * np.cos(u) * np.cos(lat)
                    y_lat = R * 1.02 * np.sin(u) * np.cos(lat)
                    z_lat = R * 1.02 * np.ones_like(u) * np.sin(lat)
                    fig.add_trace(go.Scatter3d(
                        x=x_lat, y=y_lat, z=z_lat, mode='lines',
                        line=dict(color=line_color, width=1, dash='dot'),
                        hoverinfo='skip', showlegend=False
                    ))

                # Longitudes
                for lon in np.linspace(0, 2 * np.pi, 12, endpoint=False):
                    x_lon = R * 1.02 * np.cos(lon) * np.sin(v)
                    y_lon = R * 1.02 * np.sin(lon) * np.sin(v)
                    z_lon = R * 1.02 * np.cos(v)
                    fig.add_trace(go.Scatter3d(
                        x=x_lon, y=y_lon, z=z_lon, mode='lines',
                        line=dict(color=line_color, width=1, dash='dot'),
                        hoverinfo='skip', showlegend=False
                    ))
                # --------------------------------------------------------

                # Layer 1: Active Satellites
                fig.add_trace(go.Scatter3d(
                    x=x_act, y=y_act, z=z_act,
                    mode='markers', text=names_act, hoverinfo='text',
                    marker=dict(size=2, color='#00f2fe', opacity=0.6),
                    name="Active Assets"
                ))

                # Layer 2: Lethal Debris
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
                        camera=dict(eye=dict(x=1.5, y=1.5, z=1.5)),
                        aspectmode='data'
                    ),
                    height=600
                )
                st.plotly_chart(fig, use_container_width=True)

            with tab2:
                st.write("### Data Acquisition Layer")
                search_term = st.text_input("🔍 Search Active Inventory (e.g., STARLINK, ISS, DEB)", "STARLINK")
                filtered_names = [s.name for s in sats if search_term.upper() in s.name.upper()]
                display_names = filtered_names[:50]

                if len(display_names) > 0:
                    st.table({
                        "Asset Name": display_names,
                        "Classification": [
                            "Debris" if "DEB" in name else ("SpaceX" if "STARLINK" in name else "Tracked Asset") for name in
                            display_names],
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
