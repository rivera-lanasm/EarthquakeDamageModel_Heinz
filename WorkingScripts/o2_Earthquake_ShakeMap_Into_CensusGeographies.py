# Import arcpy module
import arcpy
import os
from get_file_paths import get_shakemap_dir
from get_shakemap_files import get_shakemap_files

arcpy.env.overwriteOutput = True

## Local variables:

#ShakeMap GIS File Folder
ShakeMapDir  = get_shakemap_dir()
mi, pgv, pga = get_shakemap_files(ShakeMapDir)
# mi = "{}\mi.shp".format(ShakeMapDir)
# pgv = "{}\pgv.shp".format(ShakeMapDir)
# pga = "{}\pga.shp".format(ShakeMapDir)

#Census Geographies
#Blocks = #filepath
#Tracts = #filepath
Counties = os.path.join(os.path.dirname(os.getcwd()), 'data', 'tl_2019_us_county', 'tl_2019_us_county.shp')

#Other layers/shapefiles
arcpy.env.workspace = arcpy.GetParameterAsText(1)
WorkingDir = arcpy.env.workspace


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
arcpy.Clip_analysis(mi, Counties, WorkingDir +"\\mi_", "")
arcpy.Clip_analysis(pgv, Counties, WorkingDir +"\\pgv", "")
arcpy.Clip_analysis(pga, Counties, WorkingDir +"\\pga", "")


arcpy.AddField_management(WorkingDir +"\\mi_", "MI_int", "SHORT", "", "", "", "MI_int")
arcpy.CalculateField_management(WorkingDir +"\\mi_", "MI_int", "math.floor( !PARAMVALUE! )", "PYTHON_9.3", "")
# Dissolve mi shakemap
arcpy.Dissolve_management(WorkingDir +"\\mi_", WorkingDir +"\\mi", "MI_int", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.Delete_management(WorkingDir +"\\mi_")

#need to make layers for all of these before doing spatial join
arcpy.MakeFeatureLayer_management(mi,"mi.lyr")
arcpy.MakeFeatureLayer_management(pgv,"pgv.lyr")
arcpy.MakeFeatureLayer_management(pga,"pga.lyr")
arcpy.MakeFeatureLayer_management(Counties,"Counties.lyr")
arcpy.MakeFeatureLayer_management(Tracts,"Tracts.lyr")
arcpy.MakeFeatureLayer_management(Blocks,"Blocks.lyr")


# Select Counties That Intersect with USGS ShakeMap GIS shapefiles
arcpy.SelectLayerByLocation_management("Counties.lyr", "INTERSECT", "mi.lyr", "", "NEW_SELECTION", "NOT_INVERT")
# Make Selected Counties into New Feature Layer
arcpy.MakeFeatureLayer_management("Counties.lyr", "county_Layer", "", "", "OBJECTID OBJECTID VISIBLE NONE;\
                                  Shape Shape VISIBLE NONE;\
                                  NAME NAME VISIBLE NONE;\
                                  STATE_NAME STATE_NAME VISIBLE NONE;\
                                  STATE_FIPS STATE_FIPS VISIBLE NONE;\
                                  CNTY_FIPS CNTY_FIPS VISIBLE NONE;\
                                  FIPS FIPS VISIBLE NONE;\
                                  POPULATION POPULATION VISIBLE NONE;\
                                  POP_SQMI POP_SQMI VISIBLE NONE;\
                                  POP2010 POP2010 VISIBLE NONE;POP10_SQMI POP10_SQMI VISIBLE \
                                  NONE;WHITE WHITE VISIBLE NONE;\
                                  BLACK BLACK VISIBLE NONE;\
                                  AMERI_ES AMERI_ES VISIBLE NONE;ASIAN \
                                  ASIAN VISIBLE NONE;\
                                  HAWN_PI HAWN_PI VISIBLE NONE;\
                                  HISPANIC HISPANIC VISIBLE NONE;\
                                  OTHER OTHER VISIBLE NONE;\
                                  MULT_RACE MULT_RACE VISIBLE NONE;\
                                  MALES MALES VISIBLE NONE;\
                                  FEMALES FEMALES VISIBLE NONE;\
                                  AGE_UNDER5 AGE_UNDER5 VISIBLE NONE;\
                                  AGE_5_9 AGE_5_9 VISIBLE NONE;\
                                  AGE_10_14 AGE_10_14 VISIBLE NONE;\
                                  AGE_15_19 AGE_15_19 VISIBLE NONE;\
                                  AGE_20_24 AGE_20_24 VISIBLE NONE;\
                                  AGE_25_34 AGE_25_34 VISIBLE NONE;\
                                  AGE_35_44 AGE_35_44 VISIBLE NONE;\
                                  AGE_45_54 AGE_45_54 VISIBLE NONE;\
                                  AGE_55_64 AGE_55_64 VISIBLE NONE;\
                                  AGE_65_74 AGE_65_74 VISIBLE NONE;\
                                  AGE_75_84 AGE_75_84 VISIBLE NONE;\
                                  AGE_85_UP AGE_85_UP VISIBLE NONE;\
                                  MED_AGE MED_AGE VISIBLE NONE;\
                                  MED_AGE_M MED_AGE_M VISIBLE NONE;\
                                  MED_AGE_F MED_AGE_F VISIBLE NONE;\
                                  OUSEHOLDS HOUSEHOLDS VISIBLE NONE;\
                                  AVE_HH_SZ AVE_HH_SZ VISIBLE NONE;\
                                  HSEHLD_1_M HSEHLD_1_M VISIBLE NONE;\
                                  HSEHLD_1_F HSEHLD_1_F VISIBLE NONE;\
                                  MARHH_CHD MARHH_CHD VISIBLE NONE;\
                                  MARHH_NO_C MARHH_NO_C VISIBLE NONE;\
                                  MHH_CHILD MHH_CHILD VISIBLE NONE;\
                                  FHH_CHILD FHH_CHILD VISIBLE NONE;\
                                  FAMILIES FAMILIES VISIBLE NONE;\
                                  AVE_FAM_SZ AVE_FAM_SZ VISIBLE NONE;\
                                  HSE_UNITS HSE_UNITS VISIBLE NONE;\
                                  VACANT VACANT VISIBLE NONE;\
                                  OWNER_OCC OWNER_OCC VISIBLE NONE;\
                                  RENTER_OCC RENTER_OCC VISIBLE NONE;\
                                  NO_FARMS12 NO_FARMS12 VISIBLE NONE;\
                                  AVE_SIZE12 AVE_SIZE12 VISIBLE NONE;\
                                  CROP_ACR12 CROP_ACR12 VISIBLE NONE;\
                                  AVE_SALE12 AVE_SALE12 VISIBLE NONE;\
                                  SQMI SQMI VISIBLE NONE;\
                                  Shape_Length Shape_Length VISIBLE NONE;\
                                  Shape_Area Shape_Area VISIBLE NONE")
# Spatial Join MAX MI to each County
arcpy.SpatialJoin_analysis("county_Layer", "mi.lyr", county_max, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,county_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,county_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,county_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,county_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,county_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,county_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,county_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,county_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,county_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,county_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,county_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,county_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,county_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,county_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,county_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,county_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,county_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,county_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,county_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true \false 4 Long 0 0 ,First,#,county_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,county_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,county_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,county_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,county_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Area,-1,-1;\
                           MAX_MI \"max_MI\" true true false 14 Double 4 13 ,Max,#,mi.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGA to each County
arcpy.SpatialJoin_analysis("county_Layer", "pga.lyr", county_maxpga, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,county_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,county_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,county_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,county_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,county_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,county_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,county_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,county_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,county_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,county_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,county_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,county_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,county_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,county_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,county_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,county_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,county_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,county_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,county_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true \false 4 Long 0 0 ,First,#,county_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,county_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,county_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,county_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,county_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Area,-1,-1;\
                           MAX_PGA \"max_PGA\" true true false 14 Double 4 13 ,Max,#,pga.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGV to each County
arcpy.SpatialJoin_analysis("county_Layer", "pgv.lyr", county_maxpgv, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,county_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,county_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,county_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,county_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,county_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,county_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,county_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,county_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,county_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,county_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,county_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,county_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,county_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,county_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,county_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,county_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,county_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,county_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,county_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,county_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,county_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,county_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true \false 4 Long 0 0 ,First,#,county_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,county_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,county_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,county_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,county_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,county_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,county_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,county_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,county_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,county_Layer,Shape_Area,-1,-1;\
                           MAX_PGV \"max_PGV\" true true false 14 Double 4 13 ,Max,#,pgv.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")


# Get MI as Integer Field
arcpy.AddField_management("county_max", "MAX_MI_INT", "SHORT", "", "", "", "max_MI_int")
arcpy.CalculateField_management("county_max", "MAX_MI_INT", "math.floor( !MAX_MI! )", "PYTHON_9.3", "")


# Add PGA and PGV fields to county feature class

arcpy.JoinField_management("county_max", "FIPS", county_maxpga, "FIPS", "MAX_PGA")
arcpy.JoinField_management("county_max", "FIPS", county_maxpgv, "FIPS", "MAX_PGV")

# Delete PGA and PGV county feature classes

arcpy.Delete_management(WorkingDir + "\\county_maxpga")
arcpy.Delete_management(WorkingDir + "\\county_maxpgv")


############################### TRACTS ####################################



# Select Tracts That Intersect with USGS ShakeMap GIS shapefiles
arcpy.SelectLayerByLocation_management("Tracts.lyr", "INTERSECT", "mi.lyr", "", "NEW_SELECTION", "NOT_INVERT")
# Make Selected Tracts into New Feature Layer
arcpy.MakeFeatureLayer_management("Tracts.lyr", "tract_Layer", "", "", "OBJECTID OBJECTID VISIBLE NONE;\
Shape Shape VISIBLE NONE;STATE_FIPS STATE_FIPS VISIBLE NONE;\
                                  CNTY_FIPS CNTY_FIPS VISIBLE NONE;\
                                  STCOFIPS STCOFIPS VISIBLE NONE;\
                                  TRACT TRACT VISIBLE NONE;\
                                  FIPS FIPS VISIBLE NONE;\
                                  POPULATION POPULATION VISIBLE NONE;\
                                  POP_SQMI POP_SQMI VISIBLE NONE;\
                                  POP2010 POP2010 VISIBLE NONE;\
                                  POP10_SQMI POP10_SQMI VISIBLE NONE;\
                                  WHITE WHITE VISIBLE NONE;\
                                  BLACK BLACK VISIBLE NONE;\
                                  AMERI_ES AMERI_ES VISIBLE NONE;\
                                  ASIAN ASIAN VISIBLE NONE;\
                                  HAWN_PI HAWN_PI VISIBLE NONE;\
                                  HISPANIC HISPANIC VISIBLE NONE;\
                                  OTHER OTHER VISIBLE NONE;\
                                  MULT_RACE MULT_RACE VISIBLE NONE;\
                                  MALES MALES VISIBLE NONE;\
                                  FEMALES FEMALES VISIBLE NONE;\
                                  AGE_UNDER5 AGE_UNDER5 VISIBLE NONE;\
                                  AGE_5_9 AGE_5_9 VISIBLE NONE;\
                                  AGE_10_14 AGE_10_14 VISIBLE NONE;\
                                  AGE_15_19 AGE_15_19 VISIBLE NONE;\
                                  AGE_20_24 AGE_20_24 VISIBLE NONE;\
                                  AGE_25_34 AGE_25_34 VISIBLE NONE;\
                                  AGE_35_44 AGE_35_44 VISIBLE NONE;\
                                  AGE_45_54 AGE_45_54 VISIBLE NONE;\
                                  AGE_55_64 AGE_55_64 VISIBLE NONE;\
                                  AGE_65_74 AGE_65_74 VISIBLE NONE;\
                                  AGE_75_84 AGE_75_84 VISIBLE NONE;\
                                  AGE_85_UP AGE_85_UP VISIBLE NONE;\
                                  MED_AGE MED_AGE VISIBLE NONE;\
                                  MED_AGE_M MED_AGE_M VISIBLE NONE;\
                                  MED_AGE_F MED_AGE_F VISIBLE NONE;\
                                  HOUSEHOLDS HOUSEHOLDS VISIBLE NONE;\
                                  AVE_HH_SZ AVE_HH_SZ VISIBLE NONE;\
                                  HSEHLD_1_M HSEHLD_1_M VISIBLE NONE;\
                                  HSEHLD_1_F HSEHLD_1_F VISIBLE NONE;\
                                  MARHH_CHD MARHH_CHD VISIBLE NONE;\
                                  MARHH_NO_C MARHH_NO_C VISIBLE NONE;\
                                  MHH_CHILD MHH_CHILD VISIBLE NONE;\
                                  FHH_CHILD FHH_CHILD VISIBLE NONE;\
                                  FAMILIES FAMILIES VISIBLE NONE;\
                                  AVE_FAM_SZ AVE_FAM_SZ VISIBLE NONE;\
                                  HSE_UNITS HSE_UNITS VISIBLE NONE;\
                                  VACANT VACANT VISIBLE NONE;OWNER_OCC \
                                  OWNER_OCC VISIBLE NONE;\
                                  RENTER_OCC RENTER_OCC VISIBLE NONE;\
                                  SQMI SQMI VISIBLE NONE;\
                                  Shape_Length Shape_Length VISIBLE NONE;\
                                  Shape_Area Shape_Area VISIBLE NONE")
# Spatial Join MAX MI to each Tract
arcpy.SpatialJoin_analysis("tract_Layer", "mi.lyr", tract_max, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,tract_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,tract_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,tract_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,tract_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,tract_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,tract_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,tract_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,tract_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,tract_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,tract_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,tract_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,tract_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,tract_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,tract_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,tract_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,tract_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,tract_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Area,-1,-1;\
                           MAX_MI \"max_MI\" true true false 14 Double 4 13 ,Max,#,mi.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGA to each Tract
arcpy.SpatialJoin_analysis("tract_Layer", "pga.lyr", tract_maxpga, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,tract_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,tract_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,tract_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,tract_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,tract_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,tract_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,tract_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,tract_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,tract_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,tract_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,tract_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,tract_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,tract_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,tract_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,tract_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,tract_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,tract_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Area,-1,-1;\
                           MAX_PGA \"max_PGA\" true true false 14 Double 4 13 ,Max,#,pga.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGV to each Tract
arcpy.SpatialJoin_analysis("tract_Layer", "pgv.lyr", tract_maxpgv, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,tract_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,tract_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,tract_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,tract_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,tract_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,tract_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,tract_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,tract_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,tract_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,tract_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,tract_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,tract_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,tract_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,tract_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,tract_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,tract_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,tract_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,tract_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,tract_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,tract_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,tract_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,tract_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,tract_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,tract_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,tract_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,tract_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,tract_Layer,Shape_Area,-1,-1;\
                           MAX_PGV \"max_PGV\" true true false 14 Double 4 13 ,Max,#,pgv.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")

# Get MI as Integer Field
arcpy.AddField_management("tract_max", "MAX_MI_INT", "SHORT", "", "", "", "max_MI_int")
arcpy.CalculateField_management("tract_max", "MAX_MI_INT", "math.floor( !MAX_MI! )", "PYTHON_9.3", "")

# Add PGA and PGV fields to tract feature class

arcpy.JoinField_management("tract_max", "FIPS", tract_maxpga, "FIPS", "MAX_PGA")
arcpy.JoinField_management("tract_max", "FIPS", tract_maxpgv, "FIPS", "MAX_PGV")

# Delete PGA and PGV tract feature classes

arcpy.Delete_management(WorkingDir + "\\tract_maxpga")
arcpy.Delete_management(WorkingDir + "\\tract_maxpgv")




############################### BLOCKS ####################################



# Select Blocks That Intersect with USGS ShakeMap GIS shapefiles
arcpy.SelectLayerByLocation_management("Blocks.lyr", "INTERSECT", "mi.lyr", "", "NEW_SELECTION", "NOT_INVERT")
# Make Selected Blocks into New Feature Layer
arcpy.MakeFeatureLayer_management("Blocks.lyr", "block_Layer", "", "", "OBJECTID OBJECTID VISIBLE NONE;\
                                  Shape Shape VISIBLE NONE;\
                                  STATE_FIPS STATE_FIPS VISIBLE NONE;\
                                  CNTY_FIPS CNTY_FIPS VISIBLE NONE;\
                                  STCOFIPS STCOFIPS VISIBLE NONE;\
                                  TRACT TRACT VISIBLE NONE;\
                                  BLKGRP BLKGRP VISIBLE NONE;\
                                  FIPS FIPS VISIBLE NONE;\
                                  POPULATION POPULATION VISIBLE NONE;\
                                  POP_SQMI POP_SQMI VISIBLE NONE;\
                                  POP2010 POP2010 VISIBLE NONE;\
                                  POP10_SQMI POP10_SQMI VISIBLE NONE;\
                                  WHITE WHITE VISIBLE NONE;\
                                  BLACK BLACK VISIBLE NONE;\
                                  AMERI_ES AMERI_ES VISIBLE NONE;\
                                  ASIAN ASIAN VISIBLE NONE;\
                                  HAWN_PI HAWN_PI VISIBLE NONE;\
                                  HISPANIC HISPANIC VISIBLE NONE;\
                                  OTHER OTHER VISIBLE NONE;\
                                  MULT_RACE MULT_RACE VISIBLE NONE;\
                                  MALES MALES VISIBLE NONE;\
                                  FEMALES FEMALES VISIBLE NONE;\
                                  AGE_UNDER5 AGE_UNDER5 VISIBLE NONE;\
                                  AGE_5_9 AGE_5_9 VISIBLE NONE;\
                                  AGE_10_14 AGE_10_14 VISIBLE NONE;\
                                  AGE_15_19 AGE_15_19 VISIBLE NONE;\
                                  AGE_20_24 AGE_20_24 VISIBLE NONE;\
                                  AGE_25_34 AGE_25_34 VISIBLE NONE;\
                                  AGE_35_44 AGE_35_44 VISIBLE NONE;\
                                  AGE_45_54 AGE_45_54 VISIBLE NONE;\
                                  AGE_55_64 AGE_55_64 VISIBLE NONE;\
                                  AGE_65_74 AGE_65_74 VISIBLE NONE;\
                                  AGE_75_84 AGE_75_84 VISIBLE NONE;\
                                  AGE_85_UP AGE_85_UP VISIBLE NONE;\
                                  MED_AGE MED_AGE VISIBLE NONE;\
                                  MED_AGE_M MED_AGE_M VISIBLE NONE;\
                                  MED_AGE_F MED_AGE_F VISIBLE NONE;\
                                  HOUSEHOLDS HOUSEHOLDS VISIBLE NONE;\
                                  AVE_HH_SZ AVE_HH_SZ VISIBLE NONE;\
                                  HSEHLD_1_M HSEHLD_1_M VISIBLE NONE;\
                                  HSEHLD_1_F HSEHLD_1_F VISIBLE NONE;\
                                  MARHH_CHD MARHH_CHD VISIBLE NONE;\
                                  MARHH_NO_C MARHH_NO_C VISIBLE NONE;\
                                  MHH_CHILD MHH_CHILD VISIBLE NONE;\
                                  FHH_CHILD FHH_CHILD VISIBLE NONE;\
                                  FAMILIES FAMILIES VISIBLE NONE;\
                                  AVE_FAM_SZ AVE_FAM_SZ VISIBLE NONE;\
                                  HSE_UNITS HSE_UNITS VISIBLE NONE;\
                                  VACANT VACANT VISIBLE NONE;\
                                  OWNER_OCC OWNER_OCC VISIBLE NONE;\
                                  RENTER_OCC RENTER_OCC VISIBLE NONE;\
                                  SQMI SQMI VISIBLE NONE;\
                                  Shape_Length Shape_Length VISIBLE NONE;\
                                  Shape_Area Shape_Area VISIBLE NONE")
# Spatial Join MAX MI to each Block
arcpy.SpatialJoin_analysis("block_Layer", "mi.lyr", block_max, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,block_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,block_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,block_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,block_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,block_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,block_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,block_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,block_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,block_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,block_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,block_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,block_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,block_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,block_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,block_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,block_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,block_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,block_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,block_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,block_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,block_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,block_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,SQMI,-1,-1;\
                           Shape_Length \"Shape_Length\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Area,-1,-1;\
                           MAX_MI \"max_MI\" true true false 14 Double 4 13 ,Max,#,mi.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGA to each Block
arcpy.SpatialJoin_analysis("block_Layer", "pga.lyr", block_maxpga, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,block_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,block_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,block_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,block_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,block_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,block_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,block_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,block_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,block_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,block_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,block_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,block_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,block_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,block_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,block_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,block_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,block_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,block_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,block_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,block_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,block_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,block_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,SQMI,-1,-1;\
                           Shape_Leng \"Shape_Leng\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Area,-1,-1;\
                           MAX_PGA \"max_PGA\" true true false 14 Double 4 13 ,Max,#,pga.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")
# Spatial Join MAX PGV to each Block
arcpy.SpatialJoin_analysis("block_Layer", "pgv.lyr", block_maxpgv, "JOIN_ONE_TO_ONE", "KEEP_ALL", "STATE_FIPS \"STATE_FIPS\" true true false 2 Text 0 0 ,First,#,block_Layer,STATE_FIPS,-1,-1;\
                           CNTY_FIPS \"CNTY_FIPS\" true true false 3 Text 0 0 ,First,#,block_Layer,CNTY_FIPS,-1,-1;\
                           STCOFIPS \"STCOFIPS\" true true false 5 Text 0 0 ,First,#,block_Layer,STCOFIPS,-1,-1;\
                           TRACT \"TRACT\" true true false 6 Text 0 0 ,First,#,block_Layer,TRACT,-1,-1;\
                           BLKGRP \"BLKGRP\" true true false 1 Text 0 0 ,First,#,block_Layer,BLKGRP,-1,-1;\
                           FIPS \"FIPS\" true true false 12 Text 0 0 ,First,#,block_Layer,FIPS,-1,-1;\
                           POPULATION \"POP2015\" true true false 4 Long 0 0 ,First,#,block_Layer,POPULATION,-1,-1;\
                           POP_SQMI \"POP15_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP_SQMI,-1,-1;\
                           POP2010 \"POP2010\" true true false 4 Long 0 0 ,First,#,block_Layer,POP2010,-1,-1;\
                           POP10_SQMI \"POP10_SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,POP10_SQMI,-1,-1;\
                           WHITE \"WHITE\" true true false 4 Long 0 0 ,First,#,block_Layer,WHITE,-1,-1;\
                           BLACK \"BLACK\" true true false 4 Long 0 0 ,First,#,block_Layer,BLACK,-1,-1;\
                           AMERI_ES \"AMERI_ES\" true true false 4 Long 0 0 ,First,#,block_Layer,AMERI_ES,-1,-1;\
                           ASIAN \"ASIAN\" true true false 4 Long 0 0 ,First,#,block_Layer,ASIAN,-1,-1;\
                           HAWN_PI \"HAWN_PI\" true true false 4 Long 0 0 ,First,#,block_Layer,HAWN_PI,-1,-1;\
                           HISPANIC \"HISPANIC\" true true false 4 Long 0 0 ,First,#,block_Layer,HISPANIC,-1,-1;\
                           OTHER \"OTHER\" true true false 4 Long 0 0 ,First,#,block_Layer,OTHER,-1,-1;\
                           MULT_RACE \"MULT_RACE\" true true false 4 Long 0 0 ,First,#,block_Layer,MULT_RACE,-1,-1;\
                           MALES \"MALES\" true true false 4 Long 0 0 ,First,#,block_Layer,MALES,-1,-1;\
                           FEMALES \"FEMALES\" true true false 4 Long 0 0 ,First,#,block_Layer,FEMALES,-1,-1;\
                           AGE_UNDER5 \"AGE_UNDER5\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_UNDER5,-1,-1;\
                           AGE_5_9 \"AGE_5_9\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_5_9,-1,-1;\
                           AGE_10_14 \"AGE_10_14\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_10_14,-1,-1;\
                           AGE_15_19 \"AGE_15_19\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_15_19,-1,-1;\
                           AGE_20_24 \"AGE_20_24\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_20_24,-1,-1;\
                           AGE_25_34 \"AGE_25_34\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_25_34,-1,-1;\
                           AGE_35_44 \"AGE_35_44\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_35_44,-1,-1;\
                           AGE_45_54 \"AGE_45_54\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_45_54,-1,-1;\
                           AGE_55_64 \"AGE_55_64\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_55_64,-1,-1;\
                           AGE_65_74 \"AGE_65_74\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_65_74,-1,-1;\
                           AGE_75_84 \"AGE_75_84\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_75_84,-1,-1;\
                           AGE_85_UP \"AGE_85_UP\" true true false 4 Long 0 0 ,First,#,block_Layer,AGE_85_UP,-1,-1;\
                           MED_AGE \"MED_AGE\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE,-1,-1;\
                           MED_AGE_M \"MED_AGE_M\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_M,-1,-1;\
                           MED_AGE_F \"MED_AGE_F\" true true false 8 Double 0 0 ,First,#,block_Layer,MED_AGE_F,-1,-1;\
                           HOUSEHOLDS \"HOUSEHOLDS\" true true false 4 Long 0 0 ,First,#,block_Layer,HOUSEHOLDS,-1,-1;\
                           AVE_HH_SZ \"AVE_HH_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_HH_SZ,-1,-1;\
                           HSEHLD_1_M \"HSEHLD_1_M\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_M,-1,-1;\
                           HSEHLD_1_F \"HSEHLD_1_F\" true true false 4 Long 0 0 ,First,#,block_Layer,HSEHLD_1_F,-1,-1;\
                           MARHH_CHD \"MARHH_CHD\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_CHD,-1,-1;\
                           MARHH_NO_C \"MARHH_NO_C\" true true false 4 Long 0 0 ,First,#,block_Layer,MARHH_NO_C,-1,-1;\
                           MHH_CHILD \"MHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,MHH_CHILD,-1,-1;\
                           FHH_CHILD \"FHH_CHILD\" true true false 4 Long 0 0 ,First,#,block_Layer,FHH_CHILD,-1,-1;\
                           FAMILIES \"FAMILIES\" true true false 4 Long 0 0 ,First,#,block_Layer,FAMILIES,-1,-1;\
                           AVE_FAM_SZ \"AVE_FAM_SZ\" true true false 8 Double 0 0 ,First,#,block_Layer,AVE_FAM_SZ,-1,-1;\
                           HSE_UNITS \"HSE_UNITS\" true true false 4 Long 0 0 ,First,#,block_Layer,HSE_UNITS,-1,-1;\
                           VACANT \"VACANT\" true true false 4 Long 0 0 ,First,#,block_Layer,VACANT,-1,-1;\
                           OWNER_OCC \"OWNER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,OWNER_OCC,-1,-1;\
                           RENTER_OCC \"RENTER_OCC\" true true false 4 Long 0 0 ,First,#,block_Layer,RENTER_OCC,-1,-1;\
                           SQMI \"SQMI\" true true false 8 Double 0 0 ,First,#,block_Layer,SQMI,-1,-1;\
                           Shape_Leng \"Shape_Leng\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Length,-1,-1;\
                           Shape_Area \"Shape_Area\" false true true 8 Double 0 0 ,First,#,block_Layer,Shape_Area,-1,-1;\
                           MAX_PGV \"max_PGV\" true true false 14 Double 4 13 ,Max,#,pgv.lyr,PARAMVALUE,-1,-1", "INTERSECT", "", "")



# Get MI as Integer Field
arcpy.AddField_management("block_max", "MAX_MI_INT", "SHORT", "", "", "", "max_MI_int")
arcpy.CalculateField_management("block_max", "MAX_MI_INT", "math.floor( !MAX_MI! )", "PYTHON_9.3", "")

# Add PGA and PGV fields to block feature class

arcpy.JoinField_management("block_max", "FIPS", block_maxpga, "FIPS", "MAX_PGA")
arcpy.JoinField_management("block_max", "FIPS", block_maxpgv, "FIPS", "MAX_PGV")


# Delete PGA and PGV block feature classes

arcpy.Delete_management(WorkingDir + "\\block_maxpga")
arcpy.Delete_management(WorkingDir + "\\block_maxpgv")


# Copy over epicenter file if it exists
if os.path.exists(ShakeMapDir+"\Epicenter.shp"):
    arcpy.MakeFeatureLayer_management(ShakeMapDir+"\Epicenter.shp","Epicenter_lyr")
    arcpy.CopyFeatures_management("Epicenter_lyr", WorkingDir + "\\Epicenter")
    







