#!/usr/bin/env python
# coding: utf-8

import geopandas as gpd
import pandas as pd
import numpy as np
import fiona
import pyogrio
import os

import requests
import zipfile
import os
from io import BytesIO
from bs4 import BeautifulSoup


def read_event_data(eventid):
    """
    Read event data from a GPKG file.
    """
    event_dir = os.path.join(os.getcwd(), 'Data', 'Shakemap', eventid)

    # Update with the actual path
    GPKG_PATH = os.path.join(event_dir, "eqmodel_outputs.gpkg")

    # Read the layer you want to inspect
    # tract_shakemap_mmi, tract_shakemap_pga, tract_shakemap_pgv --> same idea
    gdf = gpd.read_file(GPKG_PATH, layer="tract_shakemap_pga")
    # make sure that only row that is not nan is the one we want
    columns = gdf.columns
    gdf = gdf[[columns[0], columns[1], columns[2], columns[3], columns[-1]]]
    # return gdf
    
    return gdf.loc[gdf[columns[1]].notna()]


# Check if a csv file for a state is exists
    # if exists, read it
    # if not, check if the gdb file exists
    # if exists, read it
def read_building_count_by_tract():
    """
    Read building count data from a CSV file.
    """
    parent_dir = os.path.dirname(os.getcwd())
    # Update with the actual path
    CSV_PATH = os.path.join(os.getcwd(), 'Data', 'building_data_csv', "aggregated_building_data.csv")
    # check if the file exists
    if not os.path.exists(CSV_PATH):
        print(f"CSV file for Building count data is not available.")
        raise ValueError
    else:
        gdf = pd.read_csv(CSV_PATH, dtype={'CENSUSCODE': str})
        gdf['CENSUSCODE'] = np.where(gdf['CENSUSCODE'].str.len() == 11, gdf['CENSUSCODE'], "0"+gdf['CENSUSCODE'])
        return gdf


# # INTERSECT WITH BUILDING STOCKS

def get_building_stock_data():
    """
    2. Check if the csv file exists
    3. If not, create the folder aand copy the csv file
    4. If exists, read the csv file
    """

    parent_dir = os.path.dirname(os.getcwd())
    # check if the folder exists
    CSV_PATH = os.path.join(os.getcwd(), 'Tables', 'Building_Percentages_Per_Tract_ALLSTATES.csv')
    
    # Change data types
    cols = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M',
            'S2H', 'S3', 'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M',
            'C1H', 'C2L', 'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M',
            'PC2H', 'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH',
            'Total']
    # create a library for data type change
    dtypes = {}
    for col in cols:
        dtypes[col] = 'float64'
    dtypes['Tract'] = 'str'
    
    if os.path.exists(CSV_PATH):
        print(f"Building stock data exists at {CSV_PATH}")
        gdf = pd.read_csv(CSV_PATH, dtype=dtypes)
        gdf = gdf.drop(columns=['Unnamed: 0'])
        gdf['CENSUSCODE'] = np.where(gdf['Tract'].str.len() == 11, gdf['Tract'], "0"+gdf['Tract'])

    else:
        print(f"Building stock data does not exist at {CSV_PATH}")
        raise ValueError
    
    return gdf


# JOIN COUNT BUILDING DATA AND BUILDING STOCK DATA

# take df_pivot and building_stock and merge them
def count_building_proportion(building_count, building_stock):
    # merge the dataframes
    merged_df = pd.merge(building_count, building_stock, on='CENSUSCODE', how='left')
    merged_df.drop(columns=['Tract'], axis=1, inplace=True)
    merged_df.drop(columns=['STATE_ID'], axis=1, inplace=True)
    #merged_df.drop(columns=['field_1'], axis=1, inplace=True)
    merged_df.bfill(inplace=True)

    # calculate the number of each building type
    cols = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M',
       'S2H', 'S3', 'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M',
       'C1H', 'C2L', 'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M',
       'PC2H', 'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH']
    for col in cols:
        merged_df[f"{col}_COUNT"] = round(merged_df[col]/merged_df['Total'] * merged_df['TOTAL_BUILDING_COUNT'])
    
    # drop the proportion columns
    merged_df.drop(columns=cols, axis=1, inplace=True)
    merged_df.drop(columns=['Total'], axis=1, inplace=True)
    
    return merged_df


# SAVE OUTPUT TO EVENT DIR

# Function to save GeoDataFrame to GeoPackage (Overwriting mode)
def save_to_geopackage(gdf, eventid, layer_name):
    """
    Saves a GeoDataFrame to the GeoPackage, overwriting the existing layer.

    Args:
        gdf (GeoDataFrame): The GeoDataFrame to save.
        layer_name (str): The name of the layer in the GeoPackage.
    """
    parent_dir = os.path.dirname(os.getcwd())
    event_dir = os.path.join(parent_dir, 'ShakeMaps', eventid)

    # Update with the actual path
    GPKG_PATH = os.path.join(event_dir, "eqmodel_outputs.gpkg")


    gdf.to_file(GPKG_PATH, layer=layer_name, driver="GPKG", mode="w")
    print(f"Saved {layer_name} to {GPKG_PATH} (overwritten).")


def building_clip_analysis(eventid):
    # overall work flow
    # 1. Read the event data
    # print(f"1. Reading event data for event ID: {eventid}")
    eventdata = read_event_data(eventid)
    # print(eventdata)

    # 2. Read the building count data
    # print("2. Reading building count data...")
    building_count = read_building_count_by_tract()
    # print(building_count)

    # 3. Read the building stock data
    # print("3. Reading building stock data...")
    building_stock = get_building_stock_data()
    # print(building_stock)

    # 4. Merge the building count and building stock data
    # print("4. Merging building count and building stock data...")
    df_output = count_building_proportion(building_count, building_stock)

    # 5. Merge the event data and the merged building count and building stock data
    # print("5. Merging event data with building data...")
    final_output = pd.merge(eventdata, df_output, left_on='GEOID', right_on='CENSUSCODE', how='left')
    final_output.ffill(inplace=True)
    final_output.drop(columns=['CENSUSCODE'], axis=1, inplace=True)
    
    # 6. Save the final output to the GeoPackage
    # print("6. Saving final output to GeoPackage...")
    # layer_name = "tract_shakemap_pga"
    # print(final_output)
    # save_to_geopackage(final_output, layer_name, eventid)
    # print(final_output.columns)
    print(f"Building clip analysis completed for event ID: {eventid}")
    
    return final_output


if __name__ == "__main__":
    # Example usage
    # Read building data and save to GeoPackage
    # building_count = read_building_count_by_tract()
    # building_stock = get_building_stock_data()
    # df_output = count_building_proportion(building_count, building_stock)
    # save_to_geopackage(df_output, layer_name="building_data")
    
    # Perform building clip analysis for a specific event ID
    eventid = 'nc72282711'
    building_clip_analysis(eventid)

