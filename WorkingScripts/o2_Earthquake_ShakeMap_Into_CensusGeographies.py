"""
This script integrates earthquake ShakeMap data with U.S. Census geographic boundaries using ArcGIS tools, including:
- Clip all USGS ShakeMap GIS shapefiles to the county layer
- Selecting Counties That Intersect with USGS ShakeMap GIS shapefiles

Using helper functions this script determines and joins maximum, minimum, and mean values of
earthquake intensity metrics (MMI, PGA, PGV) to each county and each tract

removing county data
- If we only care about tract-level PGA, PGV, and MMI, county data is NOT necessary.

"""
import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files
# import config


def shakemap_into_census_geo(eventdir): #  = config.NapaEventDir

    # ShakeMap GIS File Folder
    ShakeMapDir = get_shakemap_dir()

    mi, pgv, pga = get_shakemap_files(eventdir)
    print("mi: {}".format(mi))
    print("pgv: {}".format(pgv))
    print("pga: {}".format(pga))
    unique = eventdir.split("\\")[-1]

    #Variables for Census Geographies
    ###Blocks = #filepath
    Tracts = os.path.join(os.path.dirname(os.getcwd()), 'Data', 'tl_2019_us_tracts', '2019censustracts.shp')
    DetailCounties = os.path.join(os.path.dirname(os.getcwd()), 'Data', 'esri_2019_detailed_counties', '2019detailedcounties.shp')

    #Other layers/shapefiles
    print("eventdir: {}".format(eventdir))
    try:
        arcpy.management.CreateFileGDB(eventdir, "eqmodel_outputs")
    except arcpy.ExecuteError:
        print("eqmodel_outputs already exists in {}".format(eventdir))

    arcpy.env.workspace = os.path.join(eventdir, "eqmodel_outputs.gdb")
    GDB = os.path.join(eventdir, "eqmodel_outputs.gdb")

    # Clip all USGS ShakeMap GIS shapefiles to the county layer
    arcpy.Clip_analysis(mi, DetailCounties, os.path.join(GDB, "shakemap_countyclip_mmi"))
    arcpy.Clip_analysis(pgv, DetailCounties, os.path.join(GDB, "shakemap_countyclip_pgv"))
    arcpy.Clip_analysis(pga, DetailCounties, os.path.join(GDB, "shakemap_countyclip_pga"))


    # Add a new field (a new columns)
    arcpy.AddField_management(os.path.join(GDB, "shakemap_countyclip_mmi"), "MMI_int", "SHORT", "", "", "", "MMI_int")
    # Calculates the integers MMI value by rounding down
    arcpy.CalculateField_management(os.path.join(GDB, "shakemap_countyclip_mmi"), "MMI_int", "math.floor( !PARAMVALUE! )", "PYTHON_9.3", "")
    # Dissolves polygons that share the same MMI_int value
    arcpy.Dissolve_management(os.path.join(GDB, "shakemap_countyclip_mmi"), os.path.join(GDB, "shakemap_countyclip_mmi_int"), "MMI_int", "", "MULTI_PART", "DISSOLVE_LINES")

    # Create Layers for Spatial Analysis
    #need to make layers for all of these before doing spatial join
    arcpy.MakeFeatureLayer_management(DetailCounties,"Counties_lyr_{}".format(unique))
    arcpy.MakeFeatureLayer_management(Tracts,"Tracts_lyr_{}".format(unique))
    #arcpy.MakeFeatureLayer_management(Blocks,"Blocks_lyr_{}".format(unique))
    
    # Select Counties That Intersect with USGS ShakeMap GIS shapefiles
    SelectedCounties = arcpy.SelectLayerByLocation_management("Counties_lyr_{}".format(unique), "INTERSECT", mi, "", "NEW_SELECTION")

    def set_field_mappings_withmax(layer1, layer2, field_to_max, new_field_name):
        """

        Creates an ArcPy FieldMappings object to join two layers while computing 
        the maximum value of a specified field.
        Args:
            layer1 (str): Path to the target feature layer (usually counties)
            layer2 (str): Path to the join feature layer ()
            field_to_max (str): Name of the field for which the maximum value will be computed. ("PARAMVALUE")
            new_field_name (str): Name of the new field storing the maximum value. ( for example "max_MMI")
            
        Returns:
            arcpy.FieldMappings: Configured field mappings object with the max merge rule applied.
        """
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

    def set_field_mappings_withmin(layer1, layer2, field_to_min, new_field_name):
        """
        Creates an ArcPy FieldMappings object to join two layers while computing 
        the minimum value of a specified field.
        Args:
            layer1 (str): Path to the target feature layer.
            layer2 (str): Path to the join feature layer.
            field_to_min (str): Name of the field for which the minimum value will be computed.
            new_field_name (str): Name of the new field storing the minimum value.
            
        Returns:
            arcpy.FieldMappings: Configured field mappings object with the min merge rule applied.
        """
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(layer1) #SelectedCounties
        fieldmappings.addTable(layer2) #mmi
        FieldIndex_toMin = fieldmappings.findFieldMapIndex(field_to_min) #"PARAMVALUE"
        fieldmap = fieldmappings.getFieldMap(FieldIndex_toMin)
        field = fieldmap.outputField
        field.name = new_field_name #"min_MMI"
        field.aliasName = new_field_name #"min_MMI"
        fieldmap.outputField = field
        fieldmap.mergeRule = "min"
        fieldmappings.replaceFieldMap(FieldIndex_toMin, fieldmap)
        return fieldmappings

    def set_field_mappings_withmean(layer1, layer2, field_to_mean, new_field_name):
        fieldmappings = arcpy.FieldMappings()
        fieldmappings.addTable(layer1) #SelectedCounties
        fieldmappings.addTable(layer2) #mmi
        FieldIndex_toMean = fieldmappings.findFieldMapIndex(field_to_mean) #"PARAMVALUE"
        fieldmap = fieldmappings.getFieldMap(FieldIndex_toMean)
        field = fieldmap.outputField
        field.name = new_field_name #"mean_MMI"
        field.aliasName = new_field_name #"mean_MMI"
        fieldmap.outputField = field
        fieldmap.mergeRule = "mean"
        fieldmappings.replaceFieldMap(FieldIndex_toMean, fieldmap)
        return fieldmappings

    def remove_field_map(fieldmappings, listoffields):
        for F in listoffields:
            x = fieldmappings.findFieldMapIndex(F)
            fieldmappings.removeFieldMap(x)
        return

    # maxMMI
    fieldmappings = set_field_mappings_withmax(SelectedCounties, mi, "PARAMVALUE", "max_MMI")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX MI to each County
    arcpy.SpatialJoin_analysis(target_features = SelectedCounties,
                               join_features = mi,
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    # maxPGA
    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_county_max_mmi"), pga, "PARAMVALUE", "max_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX PGA to each County
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_county_max_mmi"),
                               join_features = pga,
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi_pga"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)


    # minPGA
    fieldmappings = set_field_mappings_withmin(os.path.join(GDB, "census_county_max_mmi_pga"), pga, "PARAMVALUE", "min_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX PGV to each County
    arcpy.SpatialJoin_analysis(target_features=os.path.join(GDB, "census_county_max_mmi_pga"),
                               join_features=pga,
                               out_feature_class=os.path.join(GDB, "census_county_max_mmi_pga_"),
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping=fieldmappings)



    # maxPGV
    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_county_max_mmi_pga_"), pgv, "PARAMVALUE", "max_PGV")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])

    # Spatial Join MAX PGV to each County
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_county_max_mmi_pga_"),
                               join_features = pgv,
                               out_feature_class = os.path.join(GDB, "census_county_max_mmi_pga_pgv"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)




    # Get MI as Integer Field
    arcpy.AddField_management(os.path.join(GDB, "census_county_max_mmi_pga_pgv"), "max_MMI_int", "SHORT", "", "", "", "max_MMI_int")
    arcpy.CalculateField_management(os.path.join(GDB, "census_county_max_mmi_pga_pgv"), "max_MMI_int", "math.floor( !max_MMI! )", "PYTHON_9.3", "")

    # Delete PGA and PGV county feature classes
    arcpy.Delete_management(os.path.join(GDB, "census_county_max_mmi_pga_"))
    arcpy.Delete_management(os.path.join(GDB, "census_county_max_mmi_pga"))
    arcpy.Delete_management(os.path.join(GDB, "census_county_max_mmi"))

    ############################### TRACTS ####################################

    # Select Tracts That Intersect with USGS ShakeMap GIS shapefiles
    SelectedTracts = arcpy.SelectLayerByLocation_management("Tracts_lyr_{}".format(unique), "INTERSECT", mi, "", "NEW_SELECTION")

    #maxMMI
    fieldmappings = set_field_mappings_withmax(SelectedTracts, mi, "PARAMVALUE", "max_MMI")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX MI to each Tract
    arcpy.SpatialJoin_analysis(target_features = SelectedTracts,
                               join_features = mi,
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)

    #maxPGA
    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_tract_max_mmi"), pga, "PARAMVALUE", "max_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGA to each Tract
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_tract_max_mmi"),
                               join_features = pga,
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi_pga"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)


    # minPGA
    fieldmappings = set_field_mappings_withmin(os.path.join(GDB, "census_tract_max_mmi_pga"), pga, "PARAMVALUE", "min_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGA to each Tract
    arcpy.SpatialJoin_analysis(target_features=os.path.join(GDB, "census_tract_max_mmi_pga"),
                               join_features=pga,
                               out_feature_class=os.path.join(GDB, "census_tract_max_mmi_pga_"),
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping=fieldmappings)

    # meanPGA
    fieldmappings = set_field_mappings_withmean(os.path.join(GDB, "census_tract_max_mmi_pga_"), pga, "PARAMVALUE", "mean_PGA")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGV to each Tract
    arcpy.SpatialJoin_analysis(target_features=os.path.join(GDB, "census_tract_max_mmi_pga_"),
                               join_features=pga,
                               out_feature_class=os.path.join(GDB, "census_tract_max_mmi_pga__"),
                               join_operation="JOIN_ONE_TO_ONE",
                               join_type="KEEP_ALL",
                               field_mapping=fieldmappings)

    #maxPGV
    fieldmappings = set_field_mappings_withmax(os.path.join(GDB, "census_tract_max_mmi_pga__"), pgv, "PARAMVALUE", "max_PGV")
    remove_field_map(fieldmappings, ["AREA", "PERIMETER", "PGAPOL_", "PGAPOL_ID", "GRID_CODE"])
    # Spatial Join MAX PGV to each Tract
    arcpy.SpatialJoin_analysis(target_features = os.path.join(GDB, "census_tract_max_mmi_pga__"),
                               join_features = pgv,
                               out_feature_class = os.path.join(GDB, "census_tract_max_mmi_pga_pgv"),
                               join_operation = "JOIN_ONE_TO_ONE",
                               join_type = "KEEP_ALL",
                               field_mapping = fieldmappings)


    # Get MI as Integer Field
    arcpy.AddField_management(os.path.join(GDB, "census_tract_max_mmi_pga_pgv"), "max_MMI_int", "SHORT", "", "", "", "max_MMI_int")
    arcpy.CalculateField_management(os.path.join(GDB, "census_tract_max_mmi_pga_pgv"), "max_MMI_int", "math.floor( !max_MMI! )", "PYTHON_9.3", "")

    # Delete PGA and PGV tract feature classes
    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi_pga__"))
    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi_pga_"))
    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi_pga"))
    arcpy.Delete_management(os.path.join(GDB, "census_tract_max_mmi"))

    # Copy over epicenter file if it exists
    if os.path.exists(os.path.join(eventdir, "Epicenter.shp")):
        #arcpy.MakeFeatureLayer_management(ShakeMapDir+"\Epicenter.shp","Epicenter_lyr")
        arcpy.CopyFeatures_management(os.path.join(eventdir, "Epicenter.shp"),os.path.join(GDB, "epicenter"))

    return

if __name__ == "__main__":
    shakemap_into_census_geo()





