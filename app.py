import streamlit as st
import plotly.graph_objects as go
from engine import fetch_orbital_inventory, get_satellite_coordinates, detect_high_risk_conjunctions, calculate_evasion_maneuver
from engine import fetch_orbital_inventory, get_satellite_coordinates, detect_high_risk_conjunctions

st.set_page_config(page_title="AstroShield AI Dashboard", layout="wide")

st.title("🛰️ AstroShield AI: Satellite Collision Prevention")

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

        # --- CREATING THE TABS ---
        tab1, tab2, tab3 = st.tabs(["🌐 3D Orbital Map", "📋 Active Inventory", "⚠️ Risk Engine Alerts"])
        with tab1:
            st.write("### Live Orbital Map (High-density shell mapping)")

            # Calculate coordinates
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

            # Format the map
            fig.update_layout(
                template="plotly_dark",
                margin=dict(l=0, r=0, b=0, t=0),
                scene=dict(
                    xaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                    zaxis=dict(showbackground=False, showgrid=False, zeroline=False, showticklabels=False),
                ),
                height=600  # Makes the map taller
            )

            st.plotly_chart(fig, use_container_width=True)

        with tab2:
            # --- THE TABLE TAB ---
            st.write("### Data Acquisition Layer")
            st.caption("Real-time list of ingested satellite telemetry.")

            # Now showing 50 satellites since we have more room!
            sat_names = [s.name for s in sats[:50]]
            st.table({"Satellite Name": sat_names, "Status": ["Protected"] * 50})

            with tab3:
                st.write("### Autonomous Risk Prediction Engine")
                st.caption("Scanning for trajectories breaching the 1e-4 threshold...")

                with st.spinner("Calculating orbital conjunctions..."):
                    alerts = detect_high_risk_conjunctions(x, y, z, names)

                    if len(alerts) > 0:
                        st.error(f"CRITICAL: {len(alerts)} high-risk conjunctions detected!")
                        st.table(alerts)

                        # --- NEW: Phase 3 Execution Layer ---
                        st.divider()
                        st.write("### Tactical Evasion Solutions")
                        st.caption("Generate optimized maneuver vectors for flagged assets.")

                        if st.button("Calculate Optimal Maneuvers"):
                            with st.spinner("Optimizing fuel consumption and calculating Delta-V..."):
                                solutions = calculate_evasion_maneuver(alerts)
                                st.success("Maneuver vectors calculated successfully.")
                                st.table(solutions)

                                # --- NEW: Command Uplink Sequence ---
                                st.divider()
                                st.write("### Command & Control Uplink")

                                # A prominent button for the operator
                                if st.button("🚀 Authorize & Uplink Maneuvers", type="primary"):
                                    import time

                                    # Simulate the telemetry upload
                                    progress_text = "Establishing secure TCP/IP uplink to LEO assets..."
                                    progress_bar = st.progress(0, text=progress_text)

                                    for percent_complete in range(100):
                                        time.sleep(0.02)  # Artificial delay for effect
                                        progress_bar.progress(percent_complete + 1,
                                                              text=f"Uploading maneuver vectors... {percent_complete + 1}%")

                                    time.sleep(0.5)
                                    progress_bar.empty()

                                    # Final confirmation
                                    st.success(
                                        "✅ TCP/IP Uplink Successful. Assets are currently executing Delta-V burns.")
                                    st.info("Satellites will return to 'Safe' status upon maneuver completion.")
                                    st.balloons()  # A little celebration for a successful test!


                    else:
                        st.success("Clear: No high-risk conjunctions detected in current orbital shell.")

