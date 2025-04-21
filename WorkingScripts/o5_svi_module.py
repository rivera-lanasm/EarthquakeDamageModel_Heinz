'''
SVI Module
'''

import os
import geopandas as gpd
import pandas as pd

#TODO: This might need to be updated if we decide to save our pipeline results in a csv
def read_event_data(eventid):
    """
    Read event data from a GPKG file.
    """
    parent_dir = os.path.dirname(os.getcwd())
    event_dir = os.path.join(parent_dir, 'ShakeMaps', eventid)
    # Update with the actual path
    GPKG_PATH = os.path.join(event_dir, "eqmodel_outputs.gpkg")
    # Read the layer you want to inspect
    gdf = gpd.read_file(GPKG_PATH, layer="tract_shakemap_pga")

    return gdf


def read_svi_data():
    # parent_dir = os.path.dirname(os.getcwd())
    svi_dir = "Data/SVI/SVI_2022_US.csv"# os.path.join(parent_dir, "Data", "SVI", "SVI_2022_US.csv")
    svi = pd.read_csv(svi_dir)

    return svi

# def process_svi(event_data, svi_data):

#     #extract only the data we need from svi
#     svi_data = svi_data[['FIPS', 'RPL_THEMES']].rename(columns={'RPL_THEMES': "SVI_Value"})

#     # Left merge event event_data and svi_data
#     # only keep tracts that are in event data
    
#     # NOTE / TODO: this might not currently work because of differences in column types.
#     # I'm waiting for us to finalize how event_data is stored before fixing this
#     #event_data_w_svi = pd.merge(event_data, svi_data, how = 'left', left_on='GEOID', right_on='FIPS')

#     return svi_data

def map_range(val):
    """
    if you have relatively high svi...30% of people living in potentially non habitable will seek shelter potentially.

        questions:
            1) under what SVI can we basically map the value to 0 --> .4 (above what value are you vulnerable?)
            2) for socially vuln, what proportion might seek shelter
    """
    if 0 <= val < 0.2:
        return 0 # 10%
    elif 0.2 <= val < 0.4:
        return 0 # 20%
    elif 0.4 <= val < 0.8:
        return .025
    elif 0.8 <= val <= 1.0:
        return .05
    else:
        return None 

def process_svi():
    
    #event_data = read_event_data(eventid)
    svi_data = read_svi_data()
    svi_data = svi_data[['FIPS', 'RPL_THEMES']].rename(columns={'RPL_THEMES': "SVI_Value"})
    #final = process_svi(event_data, svi_data = svi)
    svi_data["SVI_Value_Mapped"] = svi_data["SVI_Value"].apply(map_range)

    #TODO: potentially save this in folder directly - wait to hear back from team on desired final output
    return svi_data

# if __name__ == "__main__":
#     df = main()
#     print(df)