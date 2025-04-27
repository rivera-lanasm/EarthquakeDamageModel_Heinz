import requests
from bs4 import BeautifulSoup
import os
import zipfile
import glob
import geopandas as gpd
import pandas as pd

# URL to the Census TIGER/TRACT 2019 directory
BASE_URL = "https://www2.census.gov/geo/tiger/TIGER2024/TRACT/"

def download_census():

    # Local directories
    download_folder = os.path.join(os.getcwd(), "Data", "census_shp")
    extracted_folder = os.path.join(os.getcwd(), "Data", "extracted_census_shp")
    merged_shapefile_folder = os.path.join(os.getcwd(), "Data", "merged_shapefile")
    output_gpkg = os.path.join(merged_shapefile_folder, "Nationwide_Tracts.gpkg")

    # Ensure directories exist
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(extracted_folder, exist_ok=True)
    os.makedirs(merged_shapefile_folder, exist_ok=True)

    # check if gpkg file is found
    if not os.path.isfile(output_gpkg):
        print("no Nationwide_Tracts gpkg file found")

        # Fetch the webpage content
        print("attempting to link to {}".format(BASE_URL))
        response = requests.get(BASE_URL)
        if response.status_code != 200:
            print("Failed to access {} --> response code {}".format(BASE_URL, response.status_code))
            raise ValueError
        else:
            print("parsing...")
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        # Find all links ending with .zip
        zip_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.zip')]
        print(f"Found {len(zip_links)} ZIP files. Starting download...")

        # 1) Download each ZIP file
        print("Download Census Data to {}".format(download_folder))
        for i, zip_file in enumerate(zip_links):
            file_url = BASE_URL + zip_file
            local_path = os.path.join(download_folder, zip_file)

            print(f"Downloading {zip_file}...")
            file_response = requests.get(file_url, stream=True)

            if file_response.status_code == 200:
                with open(local_path, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
            else:
                print("Failed to download: {}, code {}".format(file_url, file_response.status_code))
                raise ValueError

        # 2) Extract all zip files
        print("Extracting ZIP files...")
        for zip_file in os.listdir(download_folder):
            if zip_file.endswith(".zip"):
                with zipfile.ZipFile(os.path.join(download_folder, zip_file), 'r') as zip_ref:
                    zip_ref.extractall(extracted_folder)
                print(f"Extracted: {zip_file}")

        # 3) Merge all shapefiles into a GeoPackage
        print("Merging CENSUS shapefiles...")

        # Recursively find all shapefiles
        shapefiles = glob.glob(os.path.join(extracted_folder, "**", "*.shp"), recursive=True)

        if not shapefiles:
            raise ValueError("No shapefiles found for merging.")

        # Read all shapefiles into GeoDataFrames and concatenate them
        gdf_list = []
        for shp in shapefiles:
            print(f"Reading {shp}...")
            gdf = gpd.read_file(shp)
            gdf_list.append(gdf)

        # Merge all GeoDataFrames
        merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=gdf_list[0].crs)

        # Save to GeoPackage (overwrite if it exists)
        merged_gdf.to_file(output_gpkg, layer="tracts", driver="GPKG")

        print(f"Nationwide Census Tracts saved to: {output_gpkg}")
    else:
        print(f"Nationwide Census Tracts already found: {output_gpkg}")

    # delete zip files (intermediate files) 
    zip_files = glob.glob(os.path.join(download_folder, "*.zip"))
    for file in zip_files:
        os.remove(file)
    # delete extracted shape files
    files = glob.glob(os.path.join(extracted_folder, "*"))
    for file in files:
        if os.path.isfile(file):
            os.remove(file)

    return None
