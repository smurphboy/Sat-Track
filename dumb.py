import math
import requests
from skyfield.api import Topos, load, wgs84, utc
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

def download_tles(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def load_tles(filename):
    satellites = load.tle_file(filename)
    return satellites

def find_satellite_passes(satellite, observer, start_time, end_time, altitude_degrees=30):
    ts = load.timescale()
    t0 = ts.utc(start_time.year, start_time.month, start_time.day)
    t1 = ts.utc(end_time.year, end_time.month, end_time.day)
    t, events = satellite.find_events(observer, t0, t1, altitude_degrees)
    event_names = 'rise above 30°', 'culminate', 'set below 30°'
    for ti, event in zip(t, events):
        name = event_names[event]
        print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)

def plot_satellite_pass(observer, satellite, start_time, end_time):
    times, azimuths, elevations = [], [], []

    ts = load.timescale()
    t = ts.utc(start_time.year, start_time.month, start_time.day,
               start_time.hour, start_time.minute, start_time.second)

    end_t = ts.utc(end_time.year, end_time.month, end_time.day,
                   end_time.hour, end_time.minute, end_time.second)

    while t < end_t:
        difference = satellite - observer
        topocentric = difference.at(t)
        alt, az, d = topocentric.altaz()
        times.append(t.utc_iso())
        azimuths.append(az.degrees)
        elevations.append(alt.degrees)
        t = t.utc_iso()[0:19]
        t = datetime.strptime(t, '%Y-%m-%dT%H:%M:%S') + timedelta(seconds=1)
        t = ts.utc(t.replace(tzinfo=utc))

    # print(azimuths, elevations, times)

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(np.deg2rad(azimuths), elevations)
    ax.grid(True)
    ax.set_rlim(bottom=90, top=0)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    titlestring = f"Satellite Pass Prediction for {satellite.name} starting {start_time}"
    plt.title(titlestring)

    plt.show()

if __name__ == "__main__":
    from datetime import timedelta

    # Replace with the URL of the TLE source
    tle_url = "https://www.celestrak.com/NORAD/elements/stations.txt"

    # Replace with the desired TLE filename
    tle_filename = "stations.tle"

    download_tles(tle_url, tle_filename)
    satellites = load_tles(tle_filename)

    # Replace with observer location (latitude, longitude, elevation)
    #observer_location = Topos(latitude_degrees=51.392028, longitude_degrees=-2.79528, elevation_m=10)
    claverham = wgs84.latlon(51.392028,-2.79528)

    # Replace with the desired satellite name
    satellite_name = "ISS (ZARYA)"

    #satellite = satellites[name=satellite_name]
    satellite = next((x for x in satellites if x.name == satellite_name), None)

    # Replace with the start and end time of the observation window
    # start_time = datetime.utcnow()
    # start_time = datetime(2024, 3, 2, 0, 15, 21, 0)
    # end_time = start_time + timedelta(minutes=10)

    # we want satellite passes for the next two days
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=2)

    find_satellite_passes(satellite, claverham, start_time, end_time, 30)

    start_time = datetime(2024, 3, 2, 0, 15, 21, 0)
    end_time = start_time + timedelta(minutes=10)
    plot_satellite_pass(claverham, satellite, start_time, end_time)