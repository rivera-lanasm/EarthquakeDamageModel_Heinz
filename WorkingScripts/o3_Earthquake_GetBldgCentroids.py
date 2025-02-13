import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files
import config


def unique_values(table, field):
    with arcpy.da.SearchCursor(table, [field]) as cursor:
        return sorted({row[0] for row in cursor})


def shakemap_get_bldgs(bldg_gdb = config.BuildingCentroids, eventdir = config.NapaEventDir):
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

    #Summarize Within Bldg Count to Tracts
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










    

