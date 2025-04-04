
from working_scripts.o1_getshakemap import FEEDURL, EVENTID
from working_scripts.o1_getshakemap import fetch_earthquake_data, retrieve_event_data, download_and_extract_shakemap

def main(**config):
    """
    config is the dictionary with user specified arguments
    
    """
    # o1 parameters
    EVENT_ID = config["event_id"]
    feed_url = FEEDURL.format(EVENTID)
    # o1 process
    jdict = fetch_earthquake_data(feed_url=feed_url)
    event = retrieve_event_data(jdict)
    download_and_extract_shakemap(event)



# if __name__ == "__main__":



