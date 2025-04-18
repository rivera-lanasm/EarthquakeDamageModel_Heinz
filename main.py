
# ========== O1 ====================================
from WorkingScripts.o1_getshakemap import FEEDURL
from WorkingScripts.o1_getshakemap import fetch_earthquake_data, retrieve_event_data, download_and_extract_shakemap
# ========== O2 ====================================
from WorkingScripts.o2_download_census import download_census
# from WorkingScripts.o2_census_intersect import download_census
# ========== O3 ====================================
from WorkingScripts.o3_clip_eventdata_buildingstocks import building_clip_analysis
from WorkingScripts.o3_get_building_structure import o3_get_building_structures
# ========== O4 ====================================

# ========== O5 ====================================
from WorkingScripts.o5_bhi import process_bhi
from WorkingScripts.o5_svi_module import process_svi

import pandas as pd

def main(**config):
    """
    config is the dictionary with user specified arguments
    
    """
    # ==============================================
    # o1 - retrieve shakemap for specified event ID
    # ==============================================
    # # o1 parameters
    # EVENT_ID = config["event_id"]
    # feed_url = FEEDURL.format(EVENT_ID)
    # # o1 process
    # jdict = fetch_earthquake_data(feed_url=feed_url)
    # event = retrieve_event_data(jdict)
    # download_and_extract_shakemap(event)
    # # extract earthquake information
    # place = jdict["properties"]["place"]
    # time = jdict["properties"]["time"]
    # mmi = jdict["properties"]["mmi"]
    # print(place)
    # print(time)
    # print(mmi)

    # ================================================
    # o2 - Download US Census Tract Data (Optional)
    # ================================================
    # download national census data if missing
    # download_census()

    # ================================================
    # o2 - Overlay US Census Tract Data onto ShakeMap
    # ================================================
    # clip census and shakemaps, min pga per census tract

    # return relevant states 

    # ================================================
    # o3 - Download Building Centroid Data (Optional)
    # ================================================


    # ================================================
    # o3 - Building Centroids
    #     Perform building clip analysis for a specific event ID
    # ================================================

    # ================================================
    # o4 - Downlaod Damage Functions (Optional) 
    # ================================================

    # ================================================
    # o4 - Downlaod Building Code Data (Optional) 
    # ================================================

    # ========================================================
    # o4 - Apply Damage Functions using Building Code Data
    # ========================================================

    # ================================================
    # o5 - Implement BHI
    # ================================================


    # ================================================
    # o6 - Download SVI data 
    # ================================================
    # download SVI (optional)
    # process SVI


    # ================================================
    # o7 - Combine SVI and BHI, Format Output Data
    # ================================================


if __name__ == "__main__":

    # USER INPUT
    # config = {"event_id": "nc72282711"}
    
    # main(**config)


    # read BHI output
    df = pd.read_csv("Data/bhi_output.csv")
    # print(df)

    # apply SVI 
    svi = process_svi()
    # print(svi)

    df = df.merge(svi, left_on = "GEOID", right_on="FIPS")
    
    df["shelter_seeking_low"] = df["shelter_seeking_low"]*df["SVI_Value_Mapped"] 

    df = df.drop(columns=["FIPS"])

    print(df["shelter_seeking_low"].sum())
    print(df["shelter_seeking_low"].sum()/df["population"].sum())

    df = df.sort_values(by=["shelter_seeking_low"], ascending=False)

    print(df.head(50))

    df.to_csv("Data/final_output.csv", index=False)



