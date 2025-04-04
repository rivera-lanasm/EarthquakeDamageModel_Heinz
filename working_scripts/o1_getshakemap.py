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

SHAKEMAP_DIR = "{}/Data".format(os.getcwd())
EVENTID = "nc72282711"
FEEDURL = "https://earthquake.usgs.gov/fdsnws/event/1/query.geojson?eventid={}"


def fetch_earthquake_data(feed_url):
    """
    Fetches earthquake data from the specified USGS GeoJSON feed.
    
    Args:
        feed_url (str): URL to the USGS earthquake feed.
        use_default (bool): Whether to use the DEFAULT_FEEDURL instead of the live feed.
    
    Returns:
        dict: Parsed JSON data from USGS or None if the request fails.
    """
    try:
        event_feed = feed_url
        response = requests.get(event_feed, timeout=10)  # Timeout to prevent hangs
        response.raise_for_status()  # Raise error for HTTP issues (e.g., 404)
        return response.json()  # Parse JSON and return as a dictionary
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {feed_url}: {e}")
        return None

def retrieve_event_data(jdict):
    """
    given usgs output from FEEDURL, parse relevant data
    """
    eventid = jdict["id"]
    magnitude = jdict["properties"]["mag"]
    # Check if ShakeMap exists
    if "shakemap" not in jdict["properties"]["products"]:
        print(f"Issue: {eventid}: No ShakeMap available.")
        print("Please check the event ID and try again")
        raise ValueError
    # retrieve lat/lon
    lon, lat = jdict["geometry"]["coordinates"][:2]
    # Store the event for further processing
    event_data = {
        "eventid": eventid,
        "magnitude": magnitude,
        "lon": lon,
        "lat": lat,
        "depth": jdict["geometry"]["coordinates"][2],
        "title": jdict["properties"]["title"],
        "time": jdict["properties"]["time"],
        "place": jdict["properties"]["place"],
        "url": jdict["properties"]["url"],
        "shakemap_url": jdict["properties"]["products"]["shakemap"][0]["contents"]["download/shape.zip"]["url"]
        }
    return event_data


def download_and_extract_shakemap(event):
    """
    Downloads and extracts the ShakeMap for a given earthquake event.

    Args:
        event (dict): Dictionary containing event details, including:
                      - event

    Returns:
        str: The path where the ShakeMap files were extracted, or None if skipped.
    """
    eventid = event["eventid"]
    event_folder = os.path.join(SHAKEMAP_DIR, eventid)

    # Check if the event folder already exists (we do NOT overwrite)
    if os.path.exists(event_folder):
        print(f"Skipping {eventid}: ShakeMap already downloaded.")
        raise ValueError

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
        raise ValueError

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
    print(f"Success! Downloaded ShakeMap for event {eventid}...")

    return event_folder  # Return the extracted folder path


if __name__ == "__main__":

    feed_url = FEEDURL.format(EVENTID)
    jdict = fetch_earthquake_data(feed_url=feed_url)

    event = retrieve_event_data(jdict)
    download_and_extract_shakemap(event)



