
# ========== O1 ====================================
from WorkingScripts.o1_getshakemap import FEEDURL
from WorkingScripts.o1_getshakemap import fetch_earthquake_data, retrieve_event_data, download_and_extract_shakemap
# ========== O2 ====================================
from WorkingScripts.o2_download_census import download_census
from WorkingScripts.o2_census_intersect import shakemap_into_census_geo
# ========== O3 ====================================
from WorkingScripts.o3_clip_eventdata_buildingstocks import building_clip_analysis
from WorkingScripts.o3_get_building_structure import o3_get_building_structures
# ========== O4 ====================================
from WorkingScripts.o4_TractLevel_DamageAssessmentModel import build_damage_estimates
# ========== O5 ====================================
from WorkingScripts.o5_bhi import process_bhi
from WorkingScripts.o5_svi_module import process_svi

import os
import pandas as pd

def main(**config):
    """
    config is the dictionary with user specified arguments
    """
    # ==============================================
    # user parameters
    # ==============================================
    EVENT_ID = config["event_id"]

    # ==============================================
    # o1 - retrieve shakemap for specified event ID
    # ==============================================
    # o1 parameters
    feed_url = FEEDURL.format(EVENT_ID)
    # o1 process
    jdict = fetch_earthquake_data(feed_url=feed_url)
    event = retrieve_event_data(jdict)
    download_and_extract_shakemap(event)
    # extract earthquake information
    # place = jdict["properties"]["place"]
    # time = jdict["properties"]["time"]
    # mmi = jdict["properties"]["mmi"]

    raise ValueError
    # ================================================
    # o2 - Download US Census Tract Shapemap (Optional)
    # ================================================    
    # download national census data if missing
    download_census()

    # ================================================
    # o2 - Overlay US Census Tract Data onto ShakeMap
    # ================================================
    # clip census and shakemaps, min pga per census tract
    event_dir = os.path.join(os.getcwd(), 'Data', EVENT_ID)
    shakemap_into_census_geo(event_dir)

    # ================================================
    # o3 - Download Building Centroid Data (Optional)
    # ================================================
    # download and extract the building data
    o3_get_building_structures()

    # ================================================
    # o3 - Building Centroids
    #     Perform building clip analysis for a specific event ID
    # ================================================
    event_results = building_clip_analysis(EVENT_ID)

    # ========================================================
    # o4 - Apply Damage Functions using Building Code Data
    # ========================================================
    o4out = build_damage_estimates(event_results)

    # ================================================
    # o5 - Implement BHI
    # ================================================
    df = process_bhi(o4out)
    df["population"] = df["population"].astype(int)
    df["shelter_seeking_low"] = df["BHI_factor_low"]*df["population"]
    df["shelter_seeking_high"] = df["BHI_factor_high"]*df["population"]
    cols = ["GEOID", "max_intensity", "population", "Total_Num_Building", "risk_level",
            "BHI_factor_low", "BHI_factor_high",
            "shelter_seeking_low", "shelter_seeking_high",
            "Total_Num_Building_Slight", "Total_Num_Building_Moderate", 
            "Total_Num_Building_Extensive", "Total_Num_Building_Complete"]
    df = df[cols]
    df["GEOID"] = df["GEOID"].astype(int)
    

    # ================================================
    # o6 - Download SVI data 
    # ================================================
    # apply SVI 
    svi = process_svi()
    svi["FIPS"] = svi["FIPS"].astype(int)
    
    # ================================================
    # o7 - Combine SVI and BHI, Format Output Data
    # ================================================
    df = df.merge(svi, left_on = "GEOID", right_on="FIPS")
    df["shelter_seeking_low"] = df["shelter_seeking_low"]*df["SVI_Value_Mapped"] 
    df["shelter_seeking_high"] = df["shelter_seeking_high"]*df["SVI_Value_Mapped"]
    df = df.drop(columns=["FIPS"])
    df.to_csv("Data/final_output.csv", index=False)




if __name__ == "__main__":
    """
    # Napa 2014: nc72282711
    # Sparta, NC, 2020: se60324281
    # 2022 humboldt county CA: nc73821036
    # puerto rico: us70006vll
    """

    # USER INPUT
    config = {"event_id": "nc73821036"}

    config = {
    "event_id": "nc73821036",
    "intensity_metric": "min", # TODO maps to "max_intensity", "min_intensity", "mean_intensity" in o4
    "BLDNG_USABILITY": {
            "Slight":{"FU":1.00,"PU":0.00,"NU":0.00},
            "Moderate":{"FU":0.87,"PU":0.13,"NU":0.00},
            "Extensive":{"FU":0.25,"PU":0.50,"NU":0.25},
            "Complete":{"FU":0.00,"PU":0.02,"NU":0.98}
            },
    "UL_SEVERITY": {
            "low": {"FU": [0.00,0.05], "PU": [0.05,0.10]},
            "medium": {"FU": [0.00,0.10], "PU": [0.30,0.50]},
            "high": {"FU": [0.10,0.30], "PU": [0.60,0.80]}
            },
    "SVI_THRESHOLD": [
                      0.000, 
                      0.025, 
                      0.050
                      ]
    }


    main(**config)





