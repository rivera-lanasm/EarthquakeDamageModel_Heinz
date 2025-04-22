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
import requests

def get_shakemap_files(eventdir):
    """
    Generate file paths for ShakeMap shapefiles in the given directory.

    Args:
        eventdir (str): Path to the ShakeMap directory. The eventdir variable gets defined and stored in get_file_paths.py

    Returns:
        tuple: Paths to 'mi.shp', 'pgv.shp', and 'pga.shp' files.
    """
    mi = os.path.join(eventdir, "mi.shp")
    pgv = os.path.join(eventdir, "pgv.shp")
    pga = os.path.join(eventdir, "pga.shp")

    # mi = "{}\mi.shp".format(eventdir)
    # pgv = "{}\pgv.shp".format(eventdir)
    # pga = "{}\pga.shp".format(eventdir)
    return mi, pgv, pga

def get_shakemap_dir():
    # Set file path to save ShakeMap zip files to

    # Check if a directory named "ShakeMaps" exists in the parent directory of the current working directory.
    # If the "ShakeMaps" directory exists, assign its path to the variable ShakeMapDir.

    # yusuf: I think this should look for the parent directory first
    # and then the current directory.  I think this is what you want.
    parent_dir = os.path.dirname(os.getcwd())
    shakemap_dir = os.path.join(parent_dir, 'ShakeMaps')
    if os.path.exists(shakemap_dir):
        ShakeMapDir = shakemap_dir

    # If the "ShakeMaps" directory does not exist, create the directory and assign the path to the variable ShakeMapDir
    else:
        os.mkdir(shakemap_dir)
        ShakeMapDir = shakemap_dir

    return ShakeMapDir


def download_census_tracts(data_dir):
    """
    Downloads and extracts the 2019 Census Tract shapefile if it does not exist.

    Args:
        data_dir (str): Path to the directory where the shapefile should be stored.

    Returns:
        str: Path to the extracted shapefile.
    """
    # url = "https://www2.census.gov/geo/tiger/TIGER2019/TRACT/tl_2019_us_tract.zip"
    # zip_path = os.path.join(data_dir, "tl_2019_us_tract.zip")
    extract_path = os.path.join(data_dir, "merged_shapefile", "Nationwide_Tracts.gpkg")

    # Check if already exists
    if os.path.exists(extract_path):
        print("Census tracts shapefile already exists {}".format(extract_path))
        return extract_path #+ r"Nationwide_Tracts.gpkg"
    else:
        print("Census tracts shapefile not found at {}".format(extract_path))
        raise ValueError

    # Download the file
    # print("Downloading Census Tracts shapefile...")
    # response = requests.get(url, stream=True)
    # response.raise_for_status()

    # with open(zip_path, "wb") as f:
    #     for chunk in response.iter_content(chunk_size=8192):
    #         f.write(chunk)

    # # Extract the ZIP file
    # with zipfile.ZipFile(zip_path, "r") as zip_ref:
    #     zip_ref.extractall(extract_path)

    # # Remove the ZIP file after extraction
    # os.remove(zip_path)

    # print("Census tracts shapefile downloaded and extracted.")
    # return os.path.join(extract_path, "tl_2019_us_tract.shp")


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

def clip_shakemap_to_tracts(shakemap_gdf, tracts_gdf, output_layer, GPKG_PATH):
    """
    Clips a ShakeMap layer to census tract boundaries using geopandas.

    Args:
        shakemap_path (str): Path to the ShakeMap shapefile (mi.shp, pga.shp, pgv.shp).
        tracts_path (str): Path to the Census Tract shapefile.
        output_layer (str): Name of the output layer to save in the GeoPackage.

    Returns:
        GeoDataFrame: Clipped GeoDataFrame.
    """
    # # Load the shapefiles
    # shakemap_gdf = gpd.read_file(shakemap_path)
    # tracts_gdf = gpd.read_file(tracts_path)

    # Convert both to the same CRS (WGS 84 - EPSG:4326)
    shakemap_gdf = shakemap_gdf.to_crs(epsg=4326)
    tracts_gdf = tracts_gdf.to_crs(epsg=4326)

    # Perform spatial intersection (clipping)
    clipped_gdf = gpd.overlay(shakemap_gdf, tracts_gdf, how="intersection")

    # Save to GeoPackage (overwrite mode)
    clipped_gdf.to_file(GPKG_PATH, layer=output_layer, driver="GPKG", mode="w")

    print(f"Saved {output_layer} (clipped ShakeMap to tracts) to {GPKG_PATH}")
    return clipped_gdf

def calculate_shakemap_statistics(shakemap_gdf, tracts_gdf, output_layer, GPKG_PATH):
    """
    Computes max, min, and mean intensity values for each tract using clipped ShakeMap data.

    Args:
        shakemap_gdf (GeoDataFrame): Clipped ShakeMap data (mi, pga, or pgv).
        tracts_gdf (GeoDataFrame): Census tract boundaries.
        output_layer (str): Name of the output layer in the GeoPackage.

    Returns:
        GeoDataFrame: Resulting GeoDataFrame with aggregated statistics.
    """
    # tracts_gdf
    # tracts_gdf = gpd.read_file(tracts_path)

    # Convert both to the same CRS before spatial join
    shakemap_gdf = shakemap_gdf.to_crs(epsg=4326)
    tracts_gdf = tracts_gdf.to_crs(epsg=4326)

    # Get the set of overlapping columns
    # common_cols = set(tracts_gdf.columns) & set(shakemap_gdf.columns)

    # # Select common columns ONLY from `tracts_gdf`, plus `geometry`
    # tracts_selected = tracts_gdf[list(common_cols) + ["geometry"]]

    # # Select unique columns from `shakemap_gdf`, plus `PARAMVALUE`
    # shakemap_selected = shakemap_gdf[[col for col in shakemap_gdf.columns if col not in common_cols or col == "PARAMVALUE"]]

    # Perform spatial join
    joined_gdf = gpd.sjoin(tracts_gdf, shakemap_gdf, how="inner", predicate="intersects")
    # drop dupes
    dupe_col = [val for val in joined_gdf.columns if "_right" in val]
    joined_gdf = joined_gdf.drop(columns=dupe_col)
    # rename
    joined_gdf.columns = [val.replace("_left","") for val in joined_gdf.columns]

    # Aggregate statistics per tract
    aggregated = joined_gdf.groupby("GEOID").agg({
        "PARAMVALUE": ["max", "min", "mean"],  # Compute max, min, and mean intensity values
        "geometry": "first"  # Keep the first geometry per tract
    }).reset_index()

    # Flatten column names
    aggregated.columns = ["GEOID", "max_intensity", "min_intensity", "mean_intensity", "geometry"]

    # Convert back to GeoDataFrame
    aggregated_gdf = gpd.GeoDataFrame(aggregated, geometry="geometry", crs=tracts_gdf.crs)

    # Save to GeoPackage (overwrite mode)
    aggregated_gdf.to_file(GPKG_PATH, layer=output_layer, driver="GPKG", mode="w")

    print(f"Saved {output_layer} (tract-level ShakeMap statistics) to {GPKG_PATH}")
    return None


def shakemap_into_census_geo(eventdir, parent_dir):
    # ShakeMap GIS File Folder
    # ShakeMapDir = get_shakemap_dir()

    mi, pgv, pga = get_shakemap_files(eventdir)
    # print("mi: {}".format(mi))
    # mi_gpd = gpd.read_file(mi)
    # print("pgv: {}".format(pgv))
    # pgv_gpd = gpd.read_file(pgv)
    pga_gpd = gpd.read_file(pga)

    # Extracts event ID from the directory path
    unique = eventdir.split("\\")[-1]  

    # Set data directory
    # parent_dir = os.getcwd()
    data_dir = os.path.join(parent_dir, 'Data')

    # Get Census Tracts file (download if missing)
    Tracts = download_census_tracts(data_dir)
    census_gpd = gpd.read_file(Tracts)

    # Define the path for the GeoPackage
    GPKG_PATH = os.path.join(eventdir, "eqmodel_outputs.gpkg")

    # Check if the GeoPackage already exists
    if os.path.exists(GPKG_PATH):
        print(f"---GeoPackage already exists: {GPKG_PATH}")
    else:
        print(f"Creating GeoPackage: {GPKG_PATH}")
        gdf = gpd.GeoDataFrame(columns=["geometry"])  # Create an empty GeoDataFrame
        gdf.to_file(GPKG_PATH, layer="init", driver="GPKG", mode="w")  # Save as an empty layer

    # Clip ShakeMap layers to census tracts
    # mi_clipped = clip_shakemap_to_tracts(mi_gpd, census_gpd, "shakemap_tractclip_mmi", GPKG_PATH)
    # pgv_clipped = clip_shakemap_to_tracts(pgv_gpd, census_gpd, "shakemap_tractclip_pgv", GPKG_PATH)
    pga_clipped = clip_shakemap_to_tracts(pga_gpd, census_gpd, "shakemap_tractclip_pga", GPKG_PATH)
    print("=======================  pga clipped ====")
    print(pga_clipped)

    ####    Now that we've clipped ShakeMap data to census tracts, 
    #       the next step is to calculate statistical 
    #       summaries (max, min, mean) for each tract. 
    # calculate_shakemap_statistics(mi_clipped, census_gpd, "tract_shakemap_mmi", GPKG_PATH)
    # calculate_shakemap_statistics(pgv_clipped, census_gpd, "tract_shakemap_pgv", GPKG_PATH)
    calculate_shakemap_statistics(pga_clipped, census_gpd, "tract_shakemap_pga", GPKG_PATH)

    return None

if __name__ == "__main__":
    """
    show stats for 2014 napa valley 
    """
    parent_dir = os.path.dirname(os.getcwd())
    event_dir = os.path.join(parent_dir, 'ShakeMaps', 'nc72282711')
    
    shakemap_into_census_geo(event_dir, parent_dir)

    # Update with the actual path
    GPKG_PATH = os.path.join(event_dir, "eqmodel_outputs.gpkg")

    # # Read the layer you want to inspect
    # tract_shakemap_gdf = gpd.read_file(GPKG_PATH, layer="tract_shakemap_mmi")

    # # Print basic information
    # print(tract_shakemap_gdf.info())
