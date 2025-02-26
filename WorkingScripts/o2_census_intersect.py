"""


Census Tract Shapefile (tl_2019_us_tracts.shp)
- Represents small geographic areas within counties.
- Typically contains 2,500 to 8,000 people per tract.
- Used for detailed demographic and statistical analysis.

County Shapefile (tl_2019_us_county.shp)
- Represents entire counties or county-equivalents (parishes, boroughs, etc.).
- Covers larger administrative areas than census tracts.
- Used for regional-level earthquake impact analysis.


"""

import os 
import geopandas as gpd

def get_shakemap_files(eventdir):
    """
    Generate file paths for ShakeMap shapefiles in the given directory.

    Args:
        eventdir (str): Path to the ShakeMap directory. The eventdir variable gets defined and stored in get_file_paths.py

    Returns:
        tuple: Paths to 'mi.shp', 'pgv.shp', and 'pga.shp' files.
    """
    
    mi = "{}\mi.shp".format(eventdir)
    pgv = "{}\pgv.shp".format(eventdir)
    pga = "{}\pga.shp".format(eventdir)
    return mi, pgv, pga

def get_shakemap_dir():
    """
    ensures that the ShakeMaps/ directory exists and returns its path.
    """
    # Set file path to save ShakeMap zip files to

    # Check if a directory named "ShakeMaps" exists in the parent directory of the current working directory.
    # If the "ShakeMaps" directory exists, assign its path to the variable ShakeMapDir.
    if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')):
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    # If the "ShakeMaps" directory does not exist, create the directory and assign the path to the variable ShakeMapDir
    else:
        os.mkdir(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps'))
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    return ShakeMapDir


def download_census_tracts(data_dir):
    """
    Downloads and extracts the 2019 Census Tract shapefile if it does not exist.

    Args:
        data_dir (str): Path to the directory where the shapefile should be stored.

    Returns:
        str: Path to the extracted shapefile.
    """
    url = "https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_us_tract.zip"
    zip_path = os.path.join(data_dir, "tl_2019_us_tract.zip")
    extract_path = os.path.join(data_dir, "tl_2019_us_tracts")

    # Check if already exists
    if os.path.exists(os.path.join(extract_path, "tl_2019_us_tract.shp")):
        print("Census tracts shapefile already exists.")
        return os.path.join(extract_path, "tl_2019_us_tract.shp")

    # Download the file
    print("Downloading Census Tracts shapefile...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    # Remove the ZIP file after extraction
    os.remove(zip_path)

    print("Census tracts shapefile downloaded and extracted.")
    return os.path.join(extract_path, "tl_2019_us_tract.shp")

def download_detailed_counties(data_dir):
    """
    Downloads and extracts the 2019 Detailed Counties shapefile if it does not exist.

    Args:
        data_dir (str): Path to the directory where the shapefile should be stored.

    Returns:
        str: Path to the extracted shapefile.
    """
    url = "https://www2.census.gov/geo/tiger/TIGER2019/COUNTY/tl_2019_us_county.zip"
    zip_path = os.path.join(data_dir, "tl_2019_us_county.zip")
    extract_path = os.path.join(data_dir, "esri_2019_detailed_counties")

    # Check if already exists
    if os.path.exists(os.path.join(extract_path, "tl_2019_us_county.shp")):
        print("Detailed counties shapefile already exists.")
        return os.path.join(extract_path, "tl_2019_us_county.shp")

    # Download the file
    print("Downloading Detailed Counties shapefile...")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(zip_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Extract the ZIP file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_path)

    # Remove the ZIP file after extraction
    os.remove(zip_path)

    print("Detailed counties shapefile downloaded and extracted.")
    return os.path.join(extract_path, "tl_2019_us_county.shp")

# Function to save GeoDataFrame to GeoPackage (Overwriting mode)
def save_to_geopackage(gdf, layer_name):
    """
    Saves a GeoDataFrame to the GeoPackage, overwriting the existing layer.

    Args:
        gdf (GeoDataFrame): The GeoDataFrame to save.
        layer_name (str): The name of the layer in the GeoPackage.
    """
    gdf.to_file(GPKG_PATH, layer=layer_name, driver="GPKG", mode="w")
    print(f"Saved {layer_name} to {GPKG_PATH} (overwritten).")

def clip_shakemap_to_tracts(shakemap_path, tracts_path, output_layer):
    """
    Clips a ShakeMap layer to census tract boundaries using geopandas.

    Args:
        shakemap_path (str): Path to the ShakeMap shapefile (mi.shp, pga.shp, pgv.shp).
        tracts_path (str): Path to the Census Tract shapefile.
        output_layer (str): Name of the output layer to save in the GeoPackage.

    Returns:
        GeoDataFrame: Clipped GeoDataFrame.
    """
    # Load the shapefiles
    shakemap_gdf = gpd.read_file(shakemap_path)
    tracts_gdf = gpd.read_file(tracts_path)

    # Perform spatial intersection (clipping)
    clipped_gdf = gpd.overlay(shakemap_gdf, tracts_gdf, how="intersection")

    # Save to GeoPackage (overwrite mode)
    clipped_gdf.to_file(GPKG_PATH, layer=output_layer, driver="GPKG", mode="w")

    print(f"Saved {output_layer} (clipped ShakeMap to tracts) to {GPKG_PATH}")
    return clipped_gdf


def shakemap_into_census_geo(eventdir):
    # ShakeMap GIS File Folder
    ShakeMapDir = get_shakemap_dir()

    mi, pgv, pga = get_shakemap_files(eventdir)
    print("mi: {}".format(mi))
    print("pgv: {}".format(pgv))
    print("pga: {}".format(pga))

    # Extracts event ID from the directory path
    unique = eventdir.split("\\")[-1]  

    # Set data directory
    data_dir = os.path.join(os.path.dirname(os.getcwd()), 'Data')

    # Get Census Tracts file (download if missing)
    Tracts = download_census_tracts(data_dir)

    # Define the path for the GeoPackage
    GPKG_PATH = os.path.join(eventdir, "eqmodel_outputs.gpkg")

    # Check if the GeoPackage already exists
    if os.path.exists(GPKG_PATH):
        print(f"GeoPackage already exists: {GPKG_PATH}")
    else:
        print(f"Creating GeoPackage: {GPKG_PATH}")
        gdf = gpd.GeoDataFrame(columns=["geometry"])  # Create an empty GeoDataFrame
        gdf.to_file(GPKG_PATH, layer="init", driver="GPKG", mode="w")  # Save as an empty layer

    # Clip ShakeMap layers to census tracts
    mi_clipped = clip_shakemap_to_tracts(mi, Tracts, "shakemap_tractclip_mmi")
    pgv_clipped = clip_shakemap_to_tracts(pgv, Tracts, "shakemap_tractclip_pgv")
    pga_clipped = clip_shakemap_to_tracts(pga, Tracts, "shakemap_tractclip_pga")

    ####    Now that we've clipped ShakeMap data to census tracts, 
    #       the next step is to calculate statistical 
    #       summaries (max, min, mean) for each tract.    


if __name__ == "__main__":
    """
    show stats for 2014 napa valley 
    """
    pass