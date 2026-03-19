import os
import requests
import pandas as pd
import numpy as np
from skyfield.api import Loader

# --- CLOUD SETUP ---
load = Loader('/tmp/skyfield_data')


# --- PHASE 1: DATA ACQUISITION LAYER ---
def fetch_orbital_inventory():
    """Fetches TLE data with an offline fallback for strict cloud firewalls."""
    url = 'https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle'
    cloud_path = '/tmp/skyfield_data/active.txt'
    
    # Bulletproof absolute path for Streamlit Cloud
    current_dir = os.path.dirname(os.path.abspath(__file__))
    backup_file = os.path.join(current_dir, 'active.txt')
    
    os.makedirs('/tmp/skyfield_data', exist_ok=True)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        # 1. Try to get the live data from Celestrak
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        with open(cloud_path, 'w') as f:
            f.write(response.text)
        satellites = load.tle_file(cloud_path)
        print("Success: Loaded live data from Celestrak.")
        
    except Exception:
        # 2. If Celestrak blocks the cloud server, use our static backup!
        print("Blocked by firewall: Falling back to offline active.txt backup.")
        satellites = load.tle_file(backup_file)
        
    return satellites


def get_satellite_coordinates(satellites, sample_size=1000):
    """Calculates real-time X, Y, Z positions for the 3D orbital map."""
    ts = load.timescale()
    t = ts.now()
    
    x_coords, y_coords, z_coords, names = [], [], [], []
    
    # Slice the list to only render a sample to prevent browser lag
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
    pass
