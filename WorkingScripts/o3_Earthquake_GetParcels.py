import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files

def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def shakemap_get_bldgs(bldg_gdb = r"C:\Data\FEMA_Lightbox_Parcels\ORNL_USAStructures_Centroids_LightboxSpatialJoin\ORNL_USAStructures_Centroids_LightboxSpatialJoin.gdb", eventdir=r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\napa2014shakemap_fortesting"):

    ShakeMapDir = get_shakemap_dir()
    mi, pgv, pga = get_shakemap_files(eventdir)
    unique = eventdir.split("\\")[-1]

    arcpy.env.workspace = os.path.join(eventdir, "eqmodel_outputs.gdb")
    GDB = os.path.join(eventdir, "eqmodel_outputs.gdb")

    #get list of intersecting states
    state_names_list = unique_values(table=os.path.join(GDB, "census_county_max_mmi_pga_pgv"), field="STATE_NAME")
    bldgs_output = os.path.join(GDB, "ORNL_LB_bldgs")

    #select building centroids that are within intersecting states and intersect them with shakemap
    remove_list = []
    for state in state_names_list:
        fc = os.path.join(bldg_gdb, state)
        if arcpy.Exists(fc):
            arcpy.management.MakeFeatureLayer(os.path.join(bldg_gdb, state), "{}_lyr".format(state))
            arcpy.management.SelectLayerByLocation("{}_lyr".format(state), 'INTERSECT', "shakemap_countyclip_mmi", "", "NEW_SELECTION")
        else:
            remove_list.append(state)

    if len(remove_list) >= 1:
        for x in remove_list:
            state_names_list.remove(x)

    if len(state_names_list) > 1:
        #merge
        arcpy.Merge_management(["{}_lyr".format(x) for x in state_names_list], bldgs_output)
    else:
        #copy features
        arcpy.CopyFeatures_management("{}_lyr".format(state), bldgs_output)

    return bldgs_output


if __name__ == "__main__":

    shakemap_get_bldgs()










    

