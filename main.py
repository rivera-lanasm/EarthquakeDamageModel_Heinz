
from working_scripts.o1_getshakemap import FEEDURL
from working_scripts.o1_getshakemap import fetch_earthquake_data, retrieve_event_data, download_and_extract_shakemap
from working_scripts.o2_download_census import download_census

def main(**config):
    """
    config is the dictionary with user specified arguments
    
    """
    # ==============================================
    # o1 - retrieve shakemap for specified event ID
    # ==============================================
    # o1 parameters
    EVENT_ID = config["event_id"]
    feed_url = FEEDURL.format(EVENT_ID)
    # o1 process
    jdict = fetch_earthquake_data(feed_url=feed_url)
    event = retrieve_event_data(jdict)
    download_and_extract_shakemap(event)
    # extract earthquake information
    place = jdict["properties"]["place"]
    time = jdict["properties"]["time"]
    mmi = jdict["properties"]["mmi"]
    print(place)
    print(time)
    print(mmi)

    # ================================================
    # o2 - Overlay US Census Tract Data onto ShakeMap
    # ================================================
    # download national census data if missing
    download_census()
    # clip census and shakemaps, min pga per census tract

    # return relevant states 

    # ================================================
    # o3 - Building Centroids
    # ================================================

    # Perform building clip analysis for a specific event ID

    # ================================================
    # o4 - Apply Damage Functions
    # ================================================

    # o4 main


if __name__ == "__main__":

    config = {"event_id": "nc72282711"}
    main(**config)


