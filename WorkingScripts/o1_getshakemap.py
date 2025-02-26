"""
Earthquake ShakeMap Retrieval and Processing Module

This module:
- fetches earthquake data from specified USGS GeoJSON feed
- filters events based on magnitude and location, 
- downloads ShakeMap shapefiles (mi, pga, pgv) 
- relevant human readable JSON metadata is saved for each event (location, etc)
    - Magnitude, location, time, depth, USGS event URL

"""


import requests
import json
import os
import zipfile
import io
import datetime
import geopandas as gpd 

SHAKEMAP_DIR = "{}\ShakeMaps".format(os.getcwd())

FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson' #Significant Events - 1 week
DEFAULT_FEEDURL = 'https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?starttime=2014-08-20%2000:00:00&endtime=2014-08-30%2000:00:00&maxlatitude=50&minlatitude=24.6&maxlongitude=-65&minlongitude=-125&minmagnitude=3&orderby=magnitude&producttype=shakemap'

TOP = 49.3457868 # north lat
LEFT = -124.7844079 # west long
RIGHT = -66.9513812 # east long
BOTTOM = 24.7433195 # south lat

def check_coords(lat, lng):
    """ Accepts a list of lat/lng tuples.
        returns the list of tuples that are within the bounding box for the US.
        NB. THESE ARE NOT NECESSARILY WITHIN THE US BORDERS!
    """
    if BOTTOM <= lat <= TOP and LEFT <= lng <= RIGHT:
        inside_box = 1
    else:
        inside_box = 0
    return inside_box


def get_shakemap_dir():
    # Set file path to save ShakeMap zip files to

    # Check if a directory named "ShakeMaps" exists in the parent directory of the current working directory.
    # If the "ShakeMaps" directory exists, assign its path to the variable ShakeMapDir.
    if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')):
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    # If the "ShakeMaps" directory does not exist, create the directory and assign the path to the variable ShakeMapDir
    else:
        os.mkdir(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps'))
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    return ShakeMapDir


def fetch_earthquake_data(feed_url, use_default=False):
    """
    Fetches earthquake data from the specified USGS GeoJSON feed.
    
    Args:
        feed_url (str): URL to the USGS earthquake feed.
        use_default (bool): Whether to use the DEFAULT_FEEDURL instead of the live feed.
    
    Returns:
        dict: Parsed JSON data from USGS or None if the request fails.
    """
    if use_default:
        print("Using DEFAULT_FEEDURL for testing.")
        feed_url = DEFAULT_FEEDURL  # Use predefined test data

    try:
        response = requests.get(feed_url, timeout=10)  # Timeout to prevent hangs
        response.raise_for_status()  # Raise error for HTTP issues (e.g., 404)
        return response.json()  # Parse JSON and return as a dictionary
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {feed_url}: {e}")
        return None

def filter_earthquake_events(jdict, mmi_threshold=3):
    """
    Filters the earthquake events based on:
    - Magnitude threshold
    - Availability of ShakeMap
    - Location within CONUS (continental US)

    Args:
        jdict (dict): Parsed earthquake data from USGS GeoJSON.
        mmi_threshold (int): Minimum intensity threshold for processing.

    Returns:
        list: Filtered list of earthquake events that pass all criteria.
    """
    if jdict is None or "features" not in jdict:
        print("No earthquake data found.")
        return []

    filtered_events = []
    
    for earthquake in jdict["features"]:
        eventid = earthquake["id"]
        magnitude = earthquake["properties"]["mag"]
        eventurl = earthquake["properties"]["detail"]

        # Skip events below magnitude threshold
        if magnitude < mmi_threshold:
            print(f"Skipping {eventid}: mag {magnitude} < {mmi_threshold}")
            continue

        # Fetch event details
        event_data = fetch_earthquake_data(eventurl)
        if event_data is None:
            print(f"Skipping {eventid}: Could not fetch event details.")
            continue

        # Check if ShakeMap exists
        if "shakemap" not in event_data["properties"]["products"]:
            print(f"Skipping {eventid}: No ShakeMap available.")
            continue

        # Check if the epicenter is within the continental US
        lon, lat = event_data["geometry"]["coordinates"][:2]
        if not check_coords(lat, lon):
            print(f"Skipping {eventid}: Epicenter not in CONUS.")
            continue

        # Store the event for further processing
        filtered_events.append({
            "eventid": eventid,
            "magnitude": magnitude,
            "lon": lon,
            "lat": lat,
            "depth": event_data["geometry"]["coordinates"][2],
            "title": event_data["properties"]["title"],
            "time": event_data["properties"]["time"],
            "place": event_data["properties"]["place"],
            "url": event_data["properties"]["url"],
            "shakemap_url": event_data["properties"]["products"]["shakemap"][0]["contents"]["download/shape.zip"]["url"]
        })

    return filtered_events


def download_and_extract_shakemap(event):
    """
    Downloads and extracts the ShakeMap for a given earthquake event.

    Args:
        event (dict): Dictionary containing event details, including:
                      - eventid
                      - shakemap_url
                      - other metadata

    Returns:
        str: The path where the ShakeMap files were extracted, or None if skipped.
    """
    eventid = event["eventid"]
    event_folder = os.path.join(SHAKEMAP_DIR, eventid)

    # Check if the event folder already exists (we do NOT overwrite)
    if os.path.exists(event_folder):
        print(f"Skipping {eventid}: ShakeMap already downloaded.")
        return None  # Skip this event

    # Ensure base directory exists
    os.makedirs(event_folder, exist_ok=True)

    # Download the ShakeMap ZIP file
    zip_path = os.path.join(event_folder, "shakemap.zip")
    try:
        print(f"Downloading ShakeMap for event {eventid}...")
        response = requests.get(event["shakemap_url"], stream=True, timeout=15)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    except requests.exceptions.RequestException as e:
        print(f"Error downloading ShakeMap for {eventid}: {e}")
        return None

    # Extract the ZIP file
    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(event_folder)
        print(f"Extracted ShakeMap for event {eventid} to {event_folder}")
    except zipfile.BadZipFile:
        print(f"Error: Invalid ZIP file for event {eventid}")
        return None

    # Remove the ZIP file after extraction
    os.remove(zip_path)

    return event_folder  # Return the extracted folder path


def save_event_metadata(event, event_folder):
    """
    Saves earthquake event metadata as a JSON file in the event folder.

    Args:
        event (dict): Dictionary containing event details.
        event_folder (str): Path where metadata should be saved.
    """
    metadata_path = os.path.join(event_folder, "metadata.json")
    
    with open(metadata_path, "w") as f:
        json.dump(event, f, indent=4)

    print(f"Metadata saved for event {event['eventid']}")


def check_for_shakemaps(mmi_threshold=3, use_default=False):
    """
    Checks for new significant earthquake ShakeMaps and downloads relevant data if available.

    Args:
        mmi_threshold (int): Minimum magnitude intensity threshold for processing events.
        use_default (bool): Whether to use the DEFAULT_FEEDURL for testing.

    Returns:
        list: A list of directories where new ShakeMap data was downloaded.
    """
    # Step 1: Fetch Earthquake Data
    jdict = fetch_earthquake_data(FEEDURL, use_default=use_default)
    if jdict is None:
        return []  # Exit early if no data is fetched

    # Step 2: Filter Relevant Earthquake Events
    filtered_events = filter_earthquake_events(jdict, mmi_threshold=mmi_threshold)

    # Step 3: Download, Extract, and Save Metadata
    new_shakemap_folders = []
    for event in filtered_events:
        event_folder = download_and_extract_shakemap(event)
        if event_folder:
            save_event_metadata(event, event_folder)
            new_shakemap_folders.append(event_folder)
        if use_default:
            break

    return new_shakemap_folders  # List of downloaded ShakeMap directories


if __name__ == "__main__":

    check_for_shakemaps(mmi_threshold=3, use_default=True)