import os
import requests
import pandas as pd
import numpy as np
from skyfield.api import Loader

# --- CLOUD SETUP ---
load = Loader('/tmp/skyfield_data')

# --- PHASE 1: DATA ACQUISITION LAYER ---
def fetch_orbital_inventory():
    """Fetches active satellites AND major debris clouds natively."""
    active_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
    debris_url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=iridium-33-debris&FORMAT=tle'
    
    active_path = '/tmp/skyfield_data/active.txt'
    debris_path = '/tmp/skyfield_data/debris.txt'
    
    # Bulletproof absolute path for Streamlit Cloud
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backup_file = os.path.join(current_dir, 'active.txt')
    
    os.makedirs('/tmp/skyfield_data', exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 1. Fetch & Parse Active Satellites safely
        response_active = requests.get(active_url, headers=headers, timeout=5)
        response_active.raise_for_status()
        with open(active_path, 'w') as f:
            f.write(response_active.text)
        active_sats = load.tle_file(active_path)
        
        # 2. Fetch & Parse the Iridium-33 Debris Cloud safely
        response_debris = requests.get(debris_url, headers=headers, timeout=5)
        response_debris.raise_for_status()
        with open(debris_path, 'w') as f:
            f.write(response_debris.text)
        debris_sats = load.tle_file(debris_path)
        
        print("Success: Loaded live Active Satellites AND Debris Cloud from Celestrak.")
        
        # 3. Combine the parsed lists! 
        # CHANGED: Debris is now added first so it never gets cut off by sample limits
        return debris_sats + active_sats
        
    except Exception as e:
        # 4. If Celestrak blocks the cloud server, use our static backup!
        print(f"Blocked by firewall: Falling back to offline active.txt backup. Error: {e}")
        satellites = load.tle_file(backup_file)
        return satellites


def get_satellite_coordinates(satellites, sample_size=None):
    """Calculates real-time X, Y, Z positions for the 3D orbital map."""
    ts = load.timescale()
    t = ts.now()
    
    x_coords, y_coords, z_coords, names = [], [], [], []
    
    # By setting sample_size to None by default, we bypass the slice limit.
    # It will process ALL loaded satellites instead of just the first 1,000.
    sats_to_process = satellites[:sample_size] if sample_size else satellites
    
    for sat in sats_to_process:
        try:
            geocentric = sat.at(t)
            pos = geocentric.position.km
            x_coords.append(pos[0])
            y_coords.append(pos[1])
            z_coords.append(pos[2])
            names.append(sat.name)
        except Exception:
            pass
            
    return x_coords, y_coords, z_coords, names


# --- PHASE 2: RISK PREDICTION ENGINE ---
import random 

def detect_high_risk_conjunctions(x_coords, y_coords, z_coords, names):
    """Simulates an AI risk prediction engine scanning for orbital conjunctions."""
    alerts = []
    
    # If the map hasn't loaded any satellites yet, return empty
    if not names:
        return alerts
        
    # Simulate finding 3 high-risk collision trajectories
    num_alerts = min(3, len(names))
    
    # Pick 3 random satellites from our loaded active list
    risky_indices = random.sample(range(len(names)), num_alerts)
    
    for idx in risky_indices:
        alerts.append({
            "Primary Asset": names[idx],
            "Threat Object": f"DEBRIS-FRAG-{random.randint(1000, 9999)}",
            "Collision Probability": f"{random.uniform(1.2, 4.5):.2f}e-4",
            "Time to Impact": f"T-Minus {random.randint(12, 90)} mins",
            "Status": "ACTION REQUIRED"
        })
        
    return alerts


# --- PHASE 3: AUTONOMOUS EXECUTION LAYER ---
def calculate_evasion_maneuver(high_risk_assets):
    """
    Simulates calculating the Delta-v and burn vectors required 
    to successfully dodge an incoming debris threat.
    """
    maneuvers = []
    
    # If there are no alerts, return empty
    if not high_risk_assets:
        return maneuvers
        
    for alert in high_risk_assets:
        # Simulate real-world orbital mechanics for the dodge
        # Delta-v is the change in velocity needed (in meters per second)
        delta_v = round(random.uniform(0.5, 3.2), 2) 
        burn_duration = random.randint(4, 15) # seconds of thruster firing
        
        # Determine the most efficient directional burn to avoid the debris
        directions = ["Prograde (Orbit Raise)", "Retrograde (Orbit Lower)", "Normal (Inclination Shift)"]
        burn_vector = random.choice(directions)
        
        maneuvers.append({
            "Target Asset": alert["Primary Asset"],
            "Evading Threat": alert["Threat Object"],
            "Burn Vector": burn_vector,
            "Required Delta-V": f"{delta_v} m/s",
            "Thruster Duration": f"{burn_duration} sec",
            "Estimated Propellant Cost": f"{round(delta_v * 0.15, 2)} kg",
            "Post-Maneuver Risk": "0.00% (Clear)"
        })
        
    return maneuvers
