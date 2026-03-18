from skyfield.api import load
import numpy as np


def fetch_orbital_inventory():
    """Fetches real-time TLE data from Celestrak."""
    stations_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
    satellites = load.tle_file(stations_url)
    print(f"Successfully loaded {len(satellites)} active satellites into IAN-SCP.")
    return satellites


def get_satellite_coordinates(satellites, sample_size=800):
    """
    Calculates the X, Y, Z coordinates for a sample of satellites.
    We use a sample size to prevent the web browser from lagging or crashing.
    """
    ts = load.timescale()
    t = ts.now()

    x, y, z = [], [], []
    names = []

    for sat in satellites[:sample_size]:
        geocentric = sat.at(t)
        pos = geocentric.position.km

        # Ensure the calculation didn't return an error/NaN
        if not np.isnan(pos[0]):
            x.append(pos[0])
            y.append(pos[1])
            z.append(pos[2])
            names.append(sat.name)

    return x, y, z, names


import math


def detect_high_risk_conjunctions(x, y, z, names, threshold_km=100):
    """
    IAN-SCP Risk Prediction Engine (Phase 2)
    Scans the current orbital shell for satellites within a dangerous proximity.
    """
    high_risk_pairs = []
    num_sats = len(names)

    # Compare every satellite to every other satellite
    for i in range(num_sats):
        for j in range(i + 1, num_sats):
            # Calculate Euclidean distance in 3D space
            dist = math.sqrt((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2 + (z[i] - z[j]) ** 2)

            # If they are closer than our threshold, flag them
            if dist < threshold_km:
                # Simulated probability math for the MVP
                prob = 1.0 / (dist ** 2) if dist > 0 else 1.0

                # Check against the project's 1e-4 threshold
                if prob >= 1e-4:
                    high_risk_pairs.append({
                        "Target Asset": names[i],
                        "Approaching Object": names[j],
                        "Distance (km)": round(dist, 2),
                        "Collision Probability": f"{prob:.2e}"
                    })

    return high_risk_pairs

