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
    backup_file = 'active.txt'  # The offline file we just added
    
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


def get_satellite_coordinates(satellites):
    """Calculates real-time X, Y, Z positions for the 3D orbital map."""
    ts = load.timescale()
    t = ts.now()
    
    x_coords, y_coords, z_coords = [], [], []
    
    for sat in satellites:
        try:
            geocentric = sat.at(t)
            pos = geocentric.position.km
            x_coords.append(pos[0])
            y_coords.append(pos[1])
            z_coords.append(pos[2])
        except Exception:
            pass
            
    return x_coords, y_coords, z_coords


# --- PHASE 2: RISK PREDICTION ENGINE ---
def detect_high_risk_conjunctions(satellites):
    pass 


# --- PHASE 3: AUTONOMOUS EXECUTION LAYER ---
def calculate_evasion_maneuver(high_risk_assets):
    pass
