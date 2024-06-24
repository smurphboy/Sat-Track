'''
Returns the next good pass of ISS over Claverham. Needs abstracting to
allow user to select location, satellite and time range and
elevation minimum for passes
'''
import csv
from datetime import datetime, timedelta
import logging
import requests
from cursesmenu import CursesMenu
from cursesmenu.items import FunctionItem, SubmenuItem, CommandItem
from skyfield.api import load, wgs84, utc
import matplotlib.pyplot as plt
import numpy as np

def download_tles(url, filename):
    '''
    Opens filename for use in load_tles
    '''
    response = requests.get(url, timeout=10)
    with open(filename, 'wb') as file:
        file.write(response.content)

def load_tles(filename):
    '''
    Returns TLEs from filename
    '''
    sats = load.tle_file(filename)
    return sats

def find_satellite_passes(satellite, observer, start_time, end_time, altitude_degrees=5):
    '''Returns satellite passes for selected sat, observer between start and end time and
    above the minimum elevation'''
    names = []
    starts = []
    ends = []
    ts = load.timescale()
    t0 = ts.utc(start_time.year, start_time.month, start_time.day)
    t1 = ts.utc(end_time.year, end_time.month, end_time.day)
    t, events = satellite.find_events(observer, t0, t1, altitude_degrees)
    event_names = 'rise above 5°', 'culminate', 'set below 5°'
    for ti, event in zip(t, events):
        name = event_names[event]
        names.append((ti.utc_strftime('%Y %b %d %H:%M:%S'), name))
        print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)
        if event==0:
            starts.append(ti)
        if event==2:
            ends.append(ti)
    return (names, starts, ends)

def plot_satellite_pass(observer, satellite, t, end_t):

    '''Plots the selected sat pass'''

    times, azimuths, elevations = [], [], []

    ts = load.timescale()
    # t = ts.utc(start_time.year, start_time.month, start_time.day,
    #            start_time.hour, start_time.minute, start_time.second)

    # end_t = ts.utc(end_time.year, end_time.month, end_time.day,
    #                end_time.hour, end_time.minute, end_time.second)
    start_t = t.utc_strftime('on %Y %b %d at %H:%M:%S')
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
    titlestring = f"Satellite Pass Prediction for {satellite.name}\nstarting {start_t}"
    plt.title(titlestring, wrap=True)
    fig.tight_layout()
    plt.show()


def select_tle():
    '''reads ./settings/tles.csv and allows user to select a source of TLEs.
    Returns the URL of the TLEs selected'''
    with open('./settings/tles.csv', encoding="utf-8", newline='', mode='r') as infile:
        reader = csv.reader(infile)
        for rows in reader:
            tles = {rows[0]:rows[1] for rows in reader}

    menu = CursesMenu.make_selection_menu(list(tles.keys()),
                                          "TLE Source",
                                          "Select TLE Source and type")
    menu.show()
    selection = menu.selected_option
    menu.refresh_screen()
    return tles[selection][1]

if __name__ == "__main__":

    logging.basicConfig(level=logging.INFO)
    # Replace with the URL of the TLE source
    TLE_URL = "https://www.celestrak.com/NORAD/elements/stations.txt"
    TLE_URL = select_tle()
    logging.info(TLE_URL)
    # Replace with the desired TLE filename
    TLE_FILENAME = "current.tle"

    download_tles(TLE_URL, TLE_FILENAME)
    satellites = load_tles(TLE_FILENAME)
    claverham = wgs84.latlon(51.392028,-2.79528)



    # Replace with the desired satellite name
    OUR_SATELLITE_NAME = "ISS (ZARYA)"

    #satellite = satellites[name=satellite_name]
    our_satellite = next((x for x in satellites if x.name == OUR_SATELLITE_NAME), None)

    # Replace with the start and end time of the observation window
    # start_time = datetime.utcnow()
    # start_time = datetime(2024, 3, 2, 0, 15, 21, 0)
    # end_time = start_time + timedelta(minutes=10)

    # we want satellite passes for the next two days
    our_start_time = datetime.now(utc)
    our_end_time = our_start_time + timedelta(days=2)
    our_names, our_starts, our_ends = find_satellite_passes(our_satellite, claverham,
                                                            our_start_time, our_end_time, 5)
    plot_satellite_pass(claverham, our_satellite, our_starts[1], our_ends[1])
