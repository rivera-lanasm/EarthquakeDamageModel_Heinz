"""
Earthquake + Building Stock Merge Module

This module:
- Reads ShakeMap-based earthquake intensity data by tract
- Loads census-based building count and structural type data
- Merges these datasets to estimate building counts by structural type per tract
- Outputs merged results for downstream damage estimation

Main Functions:
- read_event_data
- read_building_count_by_tract
- get_building_stock_data
- count_building_proportion
- save_to_geopackage
- building_clip_analysis
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd


def read_event_data(eventid):
    """
    Read event PGA data from GeoPackage for a given event ID.

    Parameters
    ----------
    eventid : str
        USGS ShakeMap event ID.

    Returns
    -------
    GeoDataFrame
        ShakeMap tract-level PGA data.
    """
    event_dir = os.path.join(os.getcwd(), 'Data', 'Shakemap', eventid)
    gpkg_path = os.path.join(event_dir, "eqmodel_outputs.gpkg")

    gdf = gpd.read_file(gpkg_path, layer="tract_shakemap_pga")
    cols = gdf.columns
    gdf = gdf[[cols[0], cols[1], cols[2], cols[3], cols[-1]]]
    return gdf.loc[gdf[cols[1]].notna()]


def read_building_count_by_tract():
    """
    Load aggregated building count data per tract.

    Returns
    -------
    DataFrame
        Building counts with CENSUSCODE as string.
    """
    csv_path = os.path.join(os.getcwd(), 'Data', 'building_data_csv', "aggregated_building_data.csv")
    if not os.path.exists(csv_path):
        raise ValueError("CSV file for building count data is not available.")

    df = pd.read_csv(csv_path, dtype={'CENSUSCODE': str})
    df['CENSUSCODE'] = np.where(df['CENSUSCODE'].str.len() == 11, df['CENSUSCODE'], "0" + df['CENSUSCODE'])
    return df


def get_building_stock_data():
    """
    Load building type proportion data per tract from preprocessed file.

    Returns
    -------
    DataFrame
        Percent share of each building type + total building count per tract.
    """
    path = os.path.join(os.getcwd(), 'Tables', 'Building_Percentages_Per_Tract_ALLSTATES.csv')

    cols = [
        'W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3', 'S4L', 'S4M', 'S4H',
        'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L', 'C2M', 'C2H', 'C3L', 'C3M', 'C3H',
        'PC1', 'PC2L', 'PC2M', 'PC2H', 'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH', 'Total'
    ]
    dtypes = {col: 'float64' for col in cols}
    dtypes['Tract'] = 'str'

    if not os.path.exists(path):
        raise ValueError(f"Building stock data not found at {path}")

    df = pd.read_csv(path, dtype=dtypes).drop(columns=["Unnamed: 0"])
    df["CENSUSCODE"] = np.where(df["Tract"].str.len() == 11, df["Tract"], "0" + df["Tract"])
    return df



def count_building_proportion(building_count, building_stock):
    """
    Merge total building counts with building stock percentages to estimate structural counts.

    Parameters
    ----------
    building_count : DataFrame
        Total buildings per tract.
    building_stock : DataFrame
        Percentages of building types per tract.

    Returns
    -------
    DataFrame
        Merged and estimated structural counts per tract.
    """
    df = pd.merge(building_count, building_stock, on='CENSUSCODE', how='left')
    df.drop(columns=['Tract', 'STATE_ID'], inplace=True)
    df.bfill(inplace=True)

    bldg_types = [col for col in building_stock.columns if col not in ['Tract', 'CENSUSCODE', 'Total']]
    for col in bldg_types:
        df[f"{col}_COUNT"] = round(df[col] / df["Total"] * df["TOTAL_BUILDING_COUNT"])

    return df.drop(columns=bldg_types + ["Total"])



def save_to_geopackage(gdf, eventid, layer_name):
    """
    Save GeoDataFrame to a GeoPackage under the given event directory and layer name.

    Parameters
    ----------
    gdf : GeoDataFrame
    eventid : str
    layer_name : str
    """
    gpkg_path = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps', eventid, "eqmodel_outputs.gpkg")
    gdf.to_file(gpkg_path, layer=layer_name, driver="GPKG", mode="w")
    print(f"Saved {layer_name} to {gpkg_path} (overwritten).")


def building_clip_analysis(eventid):
    # overall work flow
    # 1. Read the event data
    # print(f"1. Reading event data for event ID: {eventid}")
    eventdata = read_event_data(eventid)
    # print(eventdata)

    # 2. Read the building count data
    # print("2. Reading building count data...")
    building_count = read_building_count_by_tract()

    # 3. Read the building stock data
    building_stock = get_building_stock_data()

    # 4. Merge the building count and building stock data
    df_output = count_building_proportion(building_count, building_stock)

    # 5. Merge the event data and the merged building count and building stock data
    final_output = pd.merge(eventdata, df_output, left_on='GEOID', right_on='CENSUSCODE', how='left')
    final_output.ffill(inplace=True)
    final_output.drop(columns=['CENSUSCODE'], axis=1, inplace=True)
    
    print(f"Building clip analysis completed for event ID: {eventid}")
    
    return final_output


