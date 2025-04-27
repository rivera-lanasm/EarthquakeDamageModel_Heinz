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


# # Function to save GeoDataFrame to GeoPackage (Overwriting mode)
# def save_to_geopackage(gdf, layer_name):
#     """
#     Saves a GeoDataFrame to the GeoPackage, overwriting the existing layer.

#     Args:
#         gdf (GeoDataFrame): The GeoDataFrame to save.
#         layer_name (str): The name of the layer in the GeoPackage.
#     """
#     gdf.to_file(GPKG_PATH, layer=layer_name, driver="GPKG", mode="w")
#     print(f"Saved {layer_name} to {GPKG_PATH} (overwritten).")

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

    # Convert both to the same CRS before spatial join
    shakemap_gdf = shakemap_gdf.to_crs(epsg=4326)
    tracts_gdf = tracts_gdf.to_crs(epsg=4326)

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


def shakemap_into_census_geo(eventdir):
    # ShakeMap GIS File Folder

    mi, pgv, pga = get_shakemap_files(eventdir)
    pga_gpd = gpd.read_file(pga)

    # Extracts event ID from the directory path
    # unique = eventdir.split("\\")[-1]  

    # Set data directory
    data_dir = os.path.join(os.getcwd(), 'Data')

    # Get Census Tracts file (download if missing)
    # Tracts = download_census_tracts(data_dir)
    Tracts = os.path.join(data_dir, "merged_shapefile", "Nationwide_Tracts.gpkg")
    census_gpd = gpd.read_file(Tracts)

    # Define the path for the GeoPackage
    GPKG_PATH = os.path.join(eventdir, "eqmodel_outputs.gpkg")

    # Check if the GeoPackage already exists
    # if os.path.exists(GPKG_PATH):
    #     print(f"---GeoPackage already exists: {GPKG_PATH}")
    # else:
    #     print(f"Creating GeoPackage: {GPKG_PATH}")
    #     gdf = gpd.GeoDataFrame(columns=["geometry"])  # Create an empty GeoDataFrame
    #     gdf.to_file(GPKG_PATH, layer="init", driver="GPKG", mode="w")  # Save as an empty layer

    # Clip ShakeMap layers to census tracts
    pga_clipped = clip_shakemap_to_tracts(pga_gpd, census_gpd, "shakemap_tractclip_pga", GPKG_PATH)

    ####    Now that we've clipped ShakeMap data to census tracts, 
    #       the next step is to calculate statistical 
    #       summaries (max, min, mean) for each tract. 
    calculate_shakemap_statistics(pga_clipped, census_gpd, "tract_shakemap_pga", GPKG_PATH)

    return None


