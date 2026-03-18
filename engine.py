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
