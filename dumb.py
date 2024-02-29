import requests
from skyfield.api import Topos, load, wgs84, utc
import matplotlib.pyplot as plt
from datetime import datetime

def download_tles(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)

def load_tles(filename):
    satellites = load.tle_file(filename)
    return satellites

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

    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(azimuths, elevations)
    ax.grid(True)
    # plt.figure(figsize=(10, 6))
    # plt.plot(times, azimuths, label='Azimuth')
    # plt.plot(times, elevations, label='Elevation')
    plt.title('Satellite Pass Prediction')
    # plt.xlabel('Time (UTC)')
    # plt.ylabel('Angle (degrees)')
    # plt.legend()
    # plt.xticks(rotation=45)
    # plt.tight_layout()
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
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(minutes=1)

    plot_satellite_pass(claverham, satellite, start_time, end_time)