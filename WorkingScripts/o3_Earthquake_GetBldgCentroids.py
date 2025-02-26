import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files
import geopandas as gpd

# import config


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})

# = config.BuildingCentroids = config.NapaEventDir
def shakemap_get_bldgs(bldg_gdb , eventdir ):
    """
    This function selects building centroids that are within the intersecting states of the shakemap and the building structures data.
    It takes 2 arguments:
    bldg_gdb: The path to the building structures data
    eventdir: The path to the event directory

    It returns the building outputs which is the count of building affected by the shakemap in each census tract.
    """
    ShakeMapDir = get_shakemap_dir()
    mi, pgv, pga = get_shakemap_files(eventdir)
    unique = eventdir.split("\\")[-1]

    arcpy.env.workspace = os.path.join(eventdir, "eqmodel_outputs.gdb")
    GDB = os.path.join(eventdir, "eqmodel_outputs.gdb")

    # get list of intersecting states
    state_names_list = unique_values(table=os.path.join(GDB, "census_county_max_mmi_pga_pgv"), 
                                     field="STATE_NAME")
    print("state_names_list: {}".format(state_names_list)) # this has len 1
    bldgs_output = os.path.join(GDB, "ORNL_LB_bldgs")
    print("bldgs_output: {}".format(bldgs_output))
    print("bldgs_output feature count:", arcpy.GetCount_management(bldgs_output)[0])

    # select building centroids that are within intersecting states and intersect them with shakemap
    remove_list = []
    for state in state_names_list:
        # fc = os.path.join(bldg_gdb, state)
        # fc = os.path.join(bldg_gdb, "{}_Structures".format(state))
        fc = os.path.join(bldg_gdb, "CA_Structures")  # Hardcode the correct name for now

        print("fc: {}".format(fc))
        if arcpy.Exists(fc):
            print("EXISTS, fc {}".format(fc))
            # arcpy.management.MakeFeatureLayer(os.path.join(bldg_gdb, state), "{}_lyr".format(state))
                # creates an in-memory layer from a feature class, which can be used for 
                # selection and analysis without modifying the original dataset.
                # does not return a variable explicitly, but it creates an in-memory layer 
                # that can be referenced by name in subsequent ArcPy functions.
            print("MakeFeatureLayer")
            arcpy.management.MakeFeatureLayer(fc, "{}_lyr".format(state))  # Use the corrected fc variable
            # print("Active layers:", arcpy.ListLayers())

            # check both layers exist 
            print("Layer exists:", arcpy.Exists("{}_lyr".format(state)))
            print("Shakemap layer exists:", arcpy.Exists("shakemap_countyclip_mmi"))

            # Check spatial reference (projection system) of both layers, i.e. GCS_WGS_1984
            print("State layer spatial reference:", arcpy.Describe("{}_lyr".format(state)).spatialReference.name)
            print("Shakemap layer spatial reference:", arcpy.Describe("shakemap_countyclip_mmi").spatialReference.name)

            # --- Check if layers overlap
            state_extent = arcpy.Describe("{}_lyr".format(state)).extent
            shakemap_extent = arcpy.Describe("shakemap_countyclip_mmi").extent
            print("State layer extent:", state_extent)
            print("Shakemap layer extent:", shakemap_extent)
            # Check if extents overlap
            x_overlap = (state_extent.XMin < shakemap_extent.XMax) and (state_extent.XMax > shakemap_extent.XMin)
            y_overlap = (state_extent.YMin < shakemap_extent.YMax) and (state_extent.YMax > shakemap_extent.YMin)
            print("Do extents overlap?", x_overlap and y_overlap)

            # Check if the shakemap layer has any features before selection
            print("Shakemap feature count:", arcpy.GetCount_management("shakemap_countyclip_mmi")[0])
            print("Selected building count:", arcpy.GetCount_management("{}_lyr".format(state))[0])

            # Check the geometry type of the shakemap layer to confirm how it interacts with buildings
                # Shakemap geometry type: Polygon
            print("Shakemap geometry type:", arcpy.Describe("shakemap_countyclip_mmi").shapeType)
            print("Building layer geometry type:", arcpy.Describe("{}_lyr".format(state)).shapeType)

            # Check if the shakemap layer has any geometry issues
            DataIssues = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\Data\geometry_issues.txt"
            arcpy.CheckGeometry_management("shakemap_countyclip_mmi", DataIssues)
            print("Check geometry completed. See {} for issues.".format(DataIssues))

            # ---------------------------------------
            # Perform intersection test in GeoPandas
            # Define the shapefile export directory inside the event folder
            export_dir = os.path.join(eventdir, "exported_shapefiles")
            # Ensure the directory exists
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
            # Define shapefile paths
            buildings_shp = os.path.join(export_dir, f"{state}_buildings.shp")
            shakemap_shp = os.path.join(export_dir, "shakemap.shp")
            # Export selected buildings and shakemap layer as shapefiles
            arcpy.CopyFeatures_management("{}_lyr".format(state), buildings_shp)
            arcpy.CopyFeatures_management("shakemap_countyclip_mmi", shakemap_shp)
            print(f"Shapefiles exported:\n- Buildings: {buildings_shp}\n- Shakemap: {shakemap_shp}")
            # Load the shapefiles using the correct paths
            buildings = gpd.read_file(buildings_shp)
            shakemap = gpd.read_file(shakemap_shp)
            # Ensure both datasets use the same coordinate system
            buildings = buildings.to_crs(shakemap.crs)
            # Perform spatial intersection
            intersecting_buildings = gpd.sjoin(buildings, shakemap, how="inner", predicate="intersects")
            # Print results
            print("Total buildings:", len(buildings))
            print("Buildings intersecting shakemap:", len(intersecting_buildings))


            print("SelectLayerByLocation")
            arcpy.management.SelectLayerByLocation("{}_lyr".format(state), 
                                                   'INTERSECT', 
                                                   "shakemap_countyclip_mmi", 
                                                   "", 
                                                   "NEW_SELECTION")

            # arcpy.management.SelectLayerByLocation("{}_lyr".format(state), 
            #                                     'WITHIN_A_DISTANCE', 
            #                                     "shakemap_countyclip_mmi", 
            #                                     "100 Meters", 
            #                                     "NEW_SELECTION")

        else:
            remove_list.append(state)
            print("DOES NOT EXISTS, fc {}".format(fc))

    # if len(remove_list) >= 1:
    #     for x in remove_list:
    #         state_names_list.remove(x)

    if len(state_names_list) > 1:
        #merge
        arcpy.Merge_management(["{}_lyr".format(x) for x in state_names_list], bldgs_output)
    else:
        #copy features
        print("arcpy.CopyFeatures_management")
        arcpy.CopyFeatures_management("{}_lyr".format(state), bldgs_output)

    # Summarize Within Bldg Count to Tracts
    with arcpy.EnvManager(
            scratchWorkspace = GDB,
            workspace = GDB):
        arcpy.analysis.SummarizeWithin(
            os.path.join(GDB, "census_tract_max_mmi_pga_pgv"),
            bldgs_output,
            os.path.join(GDB, "census_tract_max_mmi_pga_pgv_bldgcount"),
            "KEEP_ALL", None, "ADD_SHAPE_SUM", '', None, "NO_MIN_MAJ", "NO_PERCENT", None)

    scratchgdb = os.path.join(eventdir, 'scratch.gdb')
    if arcpy.Exists(scratchgdb):
        arcpy.management.Delete(scratchgdb)

    return bldgs_output


if __name__ == "__main__":

    shakemap_get_bldgs()










    

