# Import arcpy module
import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files


def shakemap_into_census_geo(eventdir=r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\napa2014shakemap_fortesting"):

    # ShakeMap GIS File Folder
    ShakeMapDir = get_shakemap_dir()

    mi, pgv, pga = get_shakemap_files(eventdir)
    # mi = "{}\mi.shp".format(ShakeMapDir)
    # pgv = "{}\pgv.shp".format(ShakeMapDir)
    # pga = "{}\pga.shp".format(ShakeMapDir)

    #Census Geographies
    #Blocks = #filepath
    Tracts = os.path.join(os.path.dirname(os.getcwd()), 'data', 'tl_2019_us_tracts', '2019censustracts.shp')
    DetailCounties = os.path.join(os.path.dirname(os.getcwd()), 'data', 'esri_2019_detailed_counties', '2019detailedcounties.shp')


    #Other layers/shapefiles
    arcpy.management.CreateFileGDB(eventdir, "eqmodel_outputs")
    arcpy.env.workspace = os.path.join(eventdir, "eqmodel_outputs.gdb")
    GDB = os.path.join(eventdir, "eqmodel_outputs.gdb")


    block_max = "block_max"
    county_max = "county_max"
    tract_max = "tract_max"

    block_maxpga = "block_maxpga"
    block_maxpgv = "block_maxpgv"

    tract_maxpga = "tract_maxpga"
    tract_maxpgv = "tract_maxpgv"

    county_maxpga = "county_maxpga"
    county_maxpgv = "county_maxpgv"


    # Clip all USGS ShakeMap GIS shapefiles to the county layer
    arcpy.Clip_analysis(mi, DetailCounties, os.path.join(GDB, "shakemap_countyclip_mmi"))
    arcpy.Clip_analysis(pgv, DetailCounties, os.path.join(GDB, "shakemap_countyclip_pgv"))
    arcpy.Clip_analysis(pga, DetailCounties, os.path.join(GDB, "shakemap_countyclip_pga"))


    arcpy.AddField_management(os.path.join(GDB, "shakemap_countyclip_mmi"), "MMI_int", "SHORT", "", "", "", "MMI_int")
    arcpy.CalculateField_management(os.path.join(GDB, "shakemap_countyclip_mmi"), "MMI_int", "math.floor( !PARAMVALUE! )", "PYTHON_9.3", "")
    arcpy.Dissolve_management(os.path.join(GDB, "shakemap_countyclip_mmi"), os.path.join(GDB, "shakemap_countyclip_mmi_int"), "MMI_int", "", "MULTI_PART", "DISSOLVE_LINES")


    #need to make layers for all of these before doing spatial join
    arcpy.MakeFeatureLayer_management(mi,"mi_lyr")
    arcpy.MakeFeatureLayer_management(pgv,"pgv_lyr")
    arcpy.MakeFeatureLayer_management(pga,"pga_lyr")
    arcpy.MakeFeatureLayer_management(DetailCounties,"Counties_lyr")
    arcpy.MakeFeatureLayer_management(Tracts,"Tracts_lyr")
    #arcpy.MakeFeatureLayer_management(Blocks,"Blocks_lyr")


    # Select Counties That Intersect with USGS ShakeMap GIS shapefiles
    SelectedCounties = arcpy.SelectLayerByLocation_management("Counties_lyr", "INTERSECT", "mi_lyr", "", "NEW_SELECTION")

    # Create a new fieldmappings and add the two input feature classes.
    fieldmappings = arcpy.FieldMappings()
    fieldmappings.addTable(SelectedCounties)
    fieldmappings.addTable(mi)
    # First get the PARAMVALUE fieldmap. PARAMVALUE is a field in the MMI feature class.
    # Setting the field's merge rule to MAX will aggregate the values for all of the cities for
    # each state into an maximum value. The field is also renamed to be more appropriate
    # for the output.
    MMI_FieldIndex = fieldmappings.findFieldMapIndex("PARAMVALUE")
    fieldmap = fieldmappings.getFieldMap(MMI_FieldIndex)
    # Get the output field's properties as a field object
    field = fieldmap.outputField
    # Rename the field and pass the updated field object back into the field map
    field.name = "max_MMI"
    field.aliasName = "max_MMI"
    fieldmap.outputField = field
    # Set the merge rule to MAX and then replace the old fieldmap in the mappings object
    # with the updated one
    fieldmap.mergeRule = "max"
    fieldmappings.replaceFieldMap(MMI_FieldIndex, fieldmap)

    def set_field_mappings_withmax(layer1, layer2, field_to_max, new_field_name):
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(layer1) #SelectedCounties
        fieldmappings.addTable(layer2) #mmi
        FieldIndex_toMax = fieldmappings.findFieldMapIndex(field_to_max) #"PARAMVALUE"
        fieldmap = fieldmappings.getFieldMap(FieldIndex_toMax)
        field = fieldmap.outputField
        field.name = new_field_name #"max_MMI"
        field.aliasName = new_field_name #"max_MMI"
        fieldmap.outputField = field
        fieldmap.mergeRule = "max"
        fieldmappings.replaceFieldMap(FieldIndex_toMax, fieldmap)
        return fieldmappings

    def remove_field_map(fieldmappings, listoffields):
        for F in listoffields:
            x = fieldmappings.findFieldMapIndex(F)
            fieldmappings.removeFieldMap(x)
        return

    fieldmappings = set_field_mappings_withmax(SelectedCounties, mi, "PARAMVALUE", "max_MMI")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX MI to each County
    arcpy.SpatialJoin_analysis(target_features = SelectedCounties,
                               join_features = "mi_lyr",
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_county_max_mmi"), "pga_lyr", "PARAMVALUE", "max_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX PGA to each County
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_county_max_mmi"),
                               join_features = "pga_lyr",
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi_pga"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_county_max_mmi_pga"), "pgv_lyr", "PARAMVALUE", "max_PGV")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX PGV to each County
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_county_max_mmi_pga"),
                               join_features = "pgv_lyr",
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi_pga_pgv"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)


    # Get MI as Integer Field
    arcpy.AddField_management(os.path.join(GDB, "census_county_max_mmi_pga_pgv"), "max_MMI_int", "SHORT", "", "", "", "max_MMI_int")
    arcpy.CalculateField_management(os.path.join(GDB, "census_county_max_mmi_pga_pgv"), "max_MMI_int", "math.floor( !max_MMI! )", "PYTHON_9.3", "")


    # # Add PGA and PGV fields to county feature class
    #
    # arcpy.JoinField_management("county_max", "FIPS", county_maxpga, "FIPS", "MAX_PGA")
    # arcpy.JoinField_management("county_max", "FIPS", county_maxpgv, "FIPS", "MAX_PGV")

    # Delete PGA and PGV county feature classes
    arcpy.Delete_management(os.path.join(GDB, "census_county_max_mmi_pga"))
    arcpy.Delete_management(os.path.join(GDB, "census_county_max_mmi"))


    ############################### TRACTS ####################################



    # Select Tracts That Intersect with USGS ShakeMap GIS shapefiles
    SelectedTracts = arcpy.SelectLayerByLocation_management("Tracts_lyr", "INTERSECT", "mi_lyr", "", "NEW_SELECTION")

    fieldmappings = set_field_mappings_withmax(SelectedTracts, mi, "PARAMVALUE", "max_MMI")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX MI to each Tract
    arcpy.SpatialJoin_analysis(target_features = SelectedTracts,
                               join_features = "mi_lyr",
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_tract_max_mmi"), pga, "PARAMVALUE", "max_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGA to each Tract
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_tract_max_mmi"),
                               join_features = "pga_lyr",
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi_pga"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_tract_max_mmi_pga"), pga, "PARAMVALUE", "max_PGV")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGV to each Tract
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_tract_max_mmi_pga"),
                               join_features = "pgv_lyr",
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi_pga_pgv"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)
    # Get MI as Integer Field
    arcpy.AddField_management(os.path.join(GDB, "census_tract_max_mmi_pga_pgv"), "max_MMI_int", "SHORT", "", "", "", "max_MMI_int")
    arcpy.CalculateField_management(os.path.join(GDB, "census_tract_max_mmi_pga_pgv"), "max_MMI_int", "math.floor( !max_MMI! )", "PYTHON_9.3", "")

    # Delete PGA and PGV tract feature classes

    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi_pga"))
    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi"))



    # Copy over epicenter file if it exists
    if os.path.exists(os.path.join(eventdir, "Epicenter.shp")):
        arcpy.MakeFeatureLayer_management(ShakeMapDir+"\Epicenter.shp","Epicenter_lyr")
        arcpy.CopyFeatures_management(os.path.join(eventdir, "Epicenter.shp"),os.path.join(GDB, "epicenter"))
    

    return

if __name__ == "__main__":
    shakemap_into_census_geo()





