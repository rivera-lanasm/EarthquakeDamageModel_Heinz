import requests
from bs4 import BeautifulSoup
import os
import zipfile
import arcpy
import glob

if __name__ == "__main__":
    # URL to the Census TIGER/TRACT 2019 directory
    base_url = "https://www2.census.gov/geo/tiger/TIGER2019/TRACT/"

    # Local directories
    download_folder = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\census_shp"
    extracted_folder = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\extracted_census_shp"
    merged_shapefile_folder = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\merged_shapefile"
    output_shapefile = os.path.join(merged_shapefile_folder, "Nationwide_Tracts.shp")

    # Ensure directories exist
    os.makedirs(download_folder, exist_ok=True)
    os.makedirs(extracted_folder, exist_ok=True)
    os.makedirs(merged_shapefile_folder, exist_ok=True)

    # Fetch the webpage content
    response = requests.get(base_url)
    if response.status_code != 200:
        raise Exception(f"Failed to access {base_url}")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, "html.parser")

    # Find all links ending with .zip
    zip_links = [a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('.zip')]

    print(f"Found {len(zip_links)} ZIP files. Starting download...")

    # 1) Download each ZIP file
    for i, zip_file in enumerate(zip_links):
        file_url = base_url + zip_file
        local_path = os.path.join(download_folder, zip_file)

        print(f"Downloading {zip_file}...")
        file_response = requests.get(file_url, stream=True)
        
        if file_response.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in file_response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            print(f"Failed to download {zip_file}")

        if i > 2:  # Limit for testing
            break
    print("All downloads completed successfully!")

    # 2) Extract all zip files
    print("Extracting ZIP files...")
    for zip_file in os.listdir(download_folder):
        if zip_file.endswith(".zip"):
            with zipfile.ZipFile(os.path.join(download_folder, zip_file), 'r') as zip_ref:
                zip_ref.extractall(extracted_folder)
            print(f"Extracted: {zip_file}")

    # 3) Merge all shapefiles
    print("Merging shapefiles...")
    
    # Recursively find all shapefiles
    shapefiles = glob.glob(os.path.join(extracted_folder, "**", "*.shp"), recursive=True)

    if not shapefiles:
        raise ValueError("No shapefiles found for merging.")

    # Use the first shapefile as the base
    base_shapefile = shapefiles[0]
    arcpy.management.CopyFeatures(base_shapefile, output_shapefile)

    # Append all other shapefiles to the base
    for shp in shapefiles[1:]:
        print(f"Merging {shp} into {output_shapefile}...")
        arcpy.management.Append(shp, output_shapefile)
