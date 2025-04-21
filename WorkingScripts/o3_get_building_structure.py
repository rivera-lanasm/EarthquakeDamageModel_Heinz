#!/usr/bin/env python
# coding: utf-8

# # LIBARY


import geopandas as gpd
import pandas as pd
import numpy as np
#import fiona
import pyogrio
import requests
import zipfile
import os
from io import BytesIO
from bs4 import BeautifulSoup


# check if directory exist if not make it, return path
def make_data_path():
    """Create directories for data storage if they do not exist."""
    cwd = os.getcwd()
    parent = os.path.dirname(cwd)
    data_path = os.path.join(parent, 'Data')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    building_data_csv = os.path.join(data_path, 'building_data_csv')
    building_data_gdb = os.path.join(data_path, 'building_data_gdb')
    building_stock_data = os.path.join(data_path, 'building_stock_data')
    if not os.path.exists(building_data_csv):
        os.makedirs(building_data_csv)
    if not os.path.exists(building_data_gdb):
        os.makedirs(building_data_gdb)
    if not os.path.exists(building_stock_data):
        os.makedirs(building_stock_data)

    return building_data_csv, building_data_gdb, building_stock_data


# # DOWNLOAD BUILDING DATA

# This notebook is to download building data, extract it, then 
# aggregate the data to count the number of building for each census tract.
def fetch_state_links():
    """Fetches state names and their corresponding links from the webpage."""
   
    # URL of the webpage to scrape
    url = "https://disasters.geoplatform.gov/USA_Structures/"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("a", href=True)
        return {link.text.strip(): link["href"] for link in links if "Deliverable" in link["href"]}
    else:
        print("Failed to fetch the webpage. Status code:", response.status_code)
        return {}

def get_link_by_state(state_name, state_links):
    """Returns the link for a given state name."""
    return state_links.get(state_name, "State not found")   


def download_and_extract_zip(state_name, state_links):
    """Downloads and extracts a ZIP file from the given URL.
    Keyword arguments:
    state_name -- Name of the state
    state_links -- Corresponding links for each state
    """
    url = get_link_by_state(state_name, state_links)
    parent_dir = os.path.dirname(os.getcwd())
    output_dir = os.path.join(parent_dir, 'Data', 'building_data_gdb')

    response = requests.get(url, stream=True)
    if response.status_code == 200:
        os.makedirs(output_dir, exist_ok=True)
        zip_path = os.path.join(output_dir, f"{state_name}_Structures.zip")
        
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        
        os.remove(zip_path)
        print(f"Downloaded, extracted, and deleted ZIP file for {state_name} to {output_dir}")
    else:
        print("Failed to download the ZIP file.")


def gdb_path_by_state(stateid):
    """Returns the path to the GDB file for a given state ID."""
    cwd = os.getcwd()

    # get parent directory
    parent_dir = os.path.dirname(cwd)
    # get the building data directory
    building_data_directory = os.path.join(parent_dir, 'Data', 'building_data_gdb')
    # find all folder in the building data directory
    folders = [f for f in os.listdir(building_data_directory) if os.path.isdir(os.path.join(building_data_directory, f))]
    # get the folder that ends with stateid
    stateid_dir= [f for f in folders if f.endswith(f'{stateid}')][0]

    return os.path.join(building_data_directory, stateid_dir, f'{stateid}_Structures.gdb')

def get_building_data_csv(stateid):
    """Returns the path to the CSV file for a given state ID."""
    building_data_directory = os.path.join(os.path.dirname(os.getcwd()), 'Data', 'building_data_csv')

    # get the csv file
    return os.path.join(building_data_directory, f'{stateid}_building_data.csv')



# read only the specified columns
def read_cols(path):
    """Read the GDB file and return a GeoDataFrame with specified columns."""
    
    cols = ['BUILD_ID', 'OCC_CLS', 'PRIM_OCC', 'CENSUSCODE', 'LONGITUDE', 'LATITUDE']
    return gpd.read_file(path, columns=cols)
    
# only read specific columns, it can reduce the memory usage and time for each state    


def read_building_data(stateid):
    """Check if the aggregated csv file exists for the given state ID.
    If it does, return the file type and None. Do nothing.
    If it does not, read the GDB file for the state and return the file type and the GeoDataFrame.
    Kwargs:
    stateid -- State ID
    """
    
    # gdb file path
    building_data_directory = gdb_path_by_state(stateid)

    # get the csv file
    csv_path = get_building_data_csv(stateid)
    if os.path.exists(csv_path):
        print(f"Aggregated csv file found for {stateid}")
        return 'csv', None

    else:
        print(f"Reading {building_data_directory}")
        return 'gdb', read_cols(building_data_directory)


# # AGGREGATE BUILDING DATA


# function to remap OCC_CLS and PRIM_OCC
def remap_occupancy_classes(gdf):
    """Remap the occupancy classes and primary occupancy from GDB files.
    Kwargs:
    gdf -- GeoDataFrame read from the GDB file"""

    # Define the mapping dictionaries
    building_data = gdf[['BUILD_ID', 'OCC_CLS', 'PRIM_OCC', 'CENSUSCODE', 'LONGITUDE', 'LATITUDE']]
    # mapping the occupancy class
    mapping = {
        'Agriculture':'OTHER', 'Education':'OTHER', 'Residential':'RESIDENTIAL', 'Unclassified':'OTHER',
        'Commercial':'OTHER', 'Government':'OTHER', 'Industrial':'OTHER', 'Utility and Misc':'OTHER',
        'Assembly':'OTHER'
    }
    building_data['OCC_CLS'] = building_data['OCC_CLS'].map(mapping)

    # mapping the primary occupancy
    mapping = {i:'OTHER' for i in building_data['PRIM_OCC'].unique() if i not in ['Single Family Dwelling', 'Multi - Family Dwelling']}
    residential = {'Single Family Dwelling':'SINGLE FAMILY', 'Multi - Family Dwelling':'MULTI FAMILY'}
    mapping.update(residential)
    building_data['PRIM_OCC'] = building_data['PRIM_OCC'].map(mapping)
    return building_data


# function to aggregate the building counts by GEODI, OCC_CLS, PRIM_OCC
def aggregate_building_counts(gdf):
    building_data = remap_occupancy_classes(gdf)
    # group by GEODI, OCC_CLS, PRIM_OCC and sum the counts
    count_building_data = building_data.groupby(['CENSUSCODE', 'OCC_CLS', 'PRIM_OCC']).agg({'BUILD_ID':'count'}).reset_index()
    # rename the columns
    count_building_data = count_building_data.rename(columns={'BUILD_ID':'COUNT'})
    return count_building_data



def pivot_building_data(count_building_data):
    """Pivot the building data to get the count of buildings by OCC_CLS and PRIM_OCC.
    Kwargs:
    count_building_data -- DataFrame with building counts aggregated by CENSUS CODE, OCC_CLS and PRIM_OCC
    """

    df = count_building_data.copy()

    # Create a pivot table
    df_pivot = df.pivot_table(index="CENSUSCODE", columns=["OCC_CLS", "PRIM_OCC"], values="COUNT", aggfunc="sum", fill_value=0)

    # Flatten MultiIndex columns
    df_pivot.columns = [f"{col[0]}_{col[1]}" for col in df_pivot.columns]
    df_pivot = df_pivot.reset_index()
    df_pivot['TOTAL_RESIDENTIAL'] = df_pivot['RESIDENTIAL_MULTI FAMILY'] + df_pivot['RESIDENTIAL_SINGLE FAMILY'] + df_pivot['RESIDENTIAL_OTHER']
    df_pivot['TOTAL_BUILDING'] = df_pivot['TOTAL_RESIDENTIAL'] + df_pivot['OTHER_OTHER']
    return df_pivot


def aggregate_building_data():
    """Aggregate the building data for all states and save to a csv file."""
    # list all files 
    path = os.path.join(os.path.dirname(os.getcwd()), 'Data', 'building_data_csv')
    files = os.listdir(path)
    # filter the files that ends with .csv
    files = [f for f in files if f.endswith('.csv')]

    # read all the csv files and concatenate them
    dfs = []
    for file in files:
        df = pd.read_csv(os.path.join(path, file))
        # get the state id from the file name
        stateid = file.split('_')[0]
        df['STATE_ID'] = stateid
        dfs.append(df)
    # concatenate the dataframes
    building_data = pd.concat(dfs, ignore_index=True)

    # drop OTHER_SINGLE FAMILY
    building_data = building_data.drop(columns=['OTHER_SINGLE FAMILY'], errors='ignore')

    # sum all building
    building_data['TOTAL_BUILDING_COUNT'] = building_data['OTHER_OTHER'] + \
                                            building_data['RESIDENTIAL_MULTI FAMILY'] + \
                                            building_data['RESIDENTIAL_OTHER'] + \
                                            building_data['RESIDENTIAL_SINGLE FAMILY']
    
    # save the building data to a csv file
    building_data.to_csv(os.path.join(path, 'aggregated_building_data.csv'), index=False)

    return None

def o3_get_building_structures():
    """Download and extract building data for all states from the given URL."""

    # get url from webpage
    state_links = fetch_state_links()
    print(state_links["California"])

    # Iterate through the state names and download the corresponding ZIP files
    i = 1
    for state in state_links:
        if state != "California":
            continue
        if i <= 50:
            download_and_extract_zip(state, state_links)
            i += 1
        else:
            break
    
    # states data
    states_data = [
        ("Alabama", "AL"), ("Alaska", "AK"), ("Arizona", "AZ"), ("Arkansas", "AR"), ("California", "CA"), ("Colorado", "CO"), ("Connecticut", "CT"), ("Delaware", "DE"),
        ("Florida", "FL"), ("Georgia", "GA"), ("Hawaii", "HI"), ("Idaho", "ID"),
        ("Illinois", "IL"), ("Indiana", "IN"), ("Iowa", "IA"), ("Kansas", "KS"),
        ("Kentucky", "KY"), ("Louisiana", "LA"), ("Maine", "ME"), ("Maryland", "MD"),
        ("Massachusetts", "MA"), ("Michigan", "MI"), ("Minnesota", "MN"), ("Mississippi", "MS"),
        ("Missouri", "MO"), ("Montana", "MT"), ("Nebraska", "NE"), ("Nevada", "NV"),
        ("New Hampshire", "NH"), ("New Jersey", "NJ"), ("New Mexico", "NM"), ("New York", "NY"),
        ("North Carolina", "NC"), ("North Dakota", "ND"), ("Ohio", "OH"), ("Oklahoma", "OK"),
        ("Oregon", "OR"), ("Pennsylvania", "PA"), ("Rhode Island", "RI"), ("South Carolina", "SC"),
        ("South Dakota", "SD"), ("Tennessee", "TN"), ("Texas", "TX"), ("Utah", "UT"),
        ("Vermont", "VT"), ("Virginia", "VA"), ("Washington", "WA"), ("West Virginia", "WV"),
        ("Wisconsin", "WI"), ("Wyoming", "WY")]

    # read the shapefiles for all states
    for state_name, stateid in states_data:
        if state_name == "California":
            continue
        print(f"Reading building data for {state_name}")
        filetype, gdf = read_building_data(stateid)
        if filetype == 'csv':
            pass
        elif filetype == 'gdb':
            count_building_data = aggregate_building_counts(gdf)
            df_pivot = pivot_building_data(count_building_data)
            output_path = os.path.join(os.path.dirname(os.getcwd()), 'Data', 'building_data_csv', f"{stateid}_building_data.csv")
            df_pivot.to_csv(output_path, index=False)
            print(f"Saved building data for {state_name} to {output_path}")

    # concatenate all the csv files
    aggregate_building_data()

    return None


if __name__ == "__main__":
    # make the data path
    building_data_csv, building_data_gdb, building_stock_data = make_data_path()
        
    # download and extract the building data
    o3_get_building_structures()

