

import arcpy
import math
import os
import sys
import json
import shutil
import datetime
import time







## Set up variables

arcpy.env.workspace = arcpy.GetParameterAsText(0)
GDB = arcpy.env.workspace

arcpy.env.overwriteOutput = True

ShakeMapDir = arcpy.GetParameterAsText(1)
mi = "{}\mi.shp".format(ShakeMapDir)


# test to see if MI 6 exists
maxvalue = 0
with arcpy.da.SearchCursor(mi,"PARAMVALUE") as cursor:
    for row in cursor:
        valueNew = row[0]
        if valueNew > maxvalue:
            maxvalue = valueNew

if not maxvalue >= 6:
    arcpy.AddWarning('MMI not greater than 6. No significant damage expected. Exiting script.')
    sys.exit(0)


arcpy.MakeFeatureLayer_management(mi, "mi_lyr")




Parcels = arcpy.GetParameterAsText(2)

SVInational = r"\\hqmac3f1\Static\GISdata\SVI\National\SVI2014_US.shp"


arcpy.MakeFeatureLayer_management(SVInational, "SVI_lyr")

sviField = arcpy.ListFields(Parcels,"svi_total")
if len(sviField) > 0:
    Parcels_SVI = Parcels
    arcpy.MakeFeatureLayer_management(Parcels_SVI, "Parcels_lyr")
elif len(sviField) == 0:

    arcpy.MakeFeatureLayer_management(Parcels, "Parcels_lyr")
    Parcels_SVI = GDB+"\\IA_Parcels_SVI"
    arcpy.SpatialJoin_analysis("Parcels_lyr", "SVI_lyr", Parcels_SVI, "JOIN_ONE_TO_ONE", "KEEP_ALL", 'Join_Count "Join_Count" true true false 4 Long 0 0 ,First,#,Parcels_lyr,Join_Count,-1,-1;\
                               TARGET_FID "TARGET_FID" true true false 4 Long 0 0 ,First,#,Parcels_lyr,TARGET_FID,-1,-1;\
                               Join_Count_1 "Join_Count" true true false 4 Long 0 0 ,First,#,Parcels_lyr,Join_Count_1,-1,-1;\
                               TARGET_FID_1 "TARGET_FID" true true false 4 Long 0 0 ,First,#,Parcels_lyr,TARGET_FID_1,-1,-1;\
                               Join_Count_12 "Join_Count" true true false 4 Long 0 0 ,First,#,Parcels_lyr,Join_Count_12,-1,-1;\
                               TARGET_FID_12 "TARGET_FID" true true false 4 Long 0 0 ,First,#,Parcels_lyr,TARGET_FID_12,-1,-1;\
                               PARCEL_ID "PARCEL_ID" true true false 8 Double 0 0 ,First,#,Parcels_lyr,PARCEL_ID,-1,-1;\
                               APN "APN" true true false 50 Text 0 0 ,First,#,IA_Parcels,APN,-1,-1;\
                               FIPS_CODE "FIPS_CODE" true true false 5 Text 0 0 ,First,#,Parcels_lyr,FIPS_CODE,-1,-1;\
                               CENSUS_TR "CENSUS_TR" true true false 10 Text 0 0 ,First,#,Parcels_lyr,CENSUS_TR,-1,-1;\
                               BLOCK_NBR "BLOCK_NBR" true true false 5 Text 0 0 ,First,#,Parcels_lyr,BLOCK_NBR,-1,-1;\
                               LOT_NBR "LOT_NBR" true true false 5 Text 0 0 ,First,#,Parcels_lyr,LOT_NBR,-1,-1;\
                               RANGE "RANGE" true true false 3 Text 0 0 ,First,#,Parcels_lyr,RANGE,-1,-1;\
                               TOWNSHIP "TOWNSHIP" true true false 3 Text 0 0 ,First,#,Parcels_lyr,TOWNSHIP,-1,-1;\
                               SECTION "SECTION" true true false 3 Text 0 0 ,First,#,Parcels_lyr,SECTION,-1,-1;\
                               LATITUDE "LATITUDE" true true false 8 Double 0 0 ,First,#,Parcels_lyr,LATITUDE,-1,-1;\
                               LONGITUDE "LONGITUDE" true true false 8 Double 0 0 ,First,#,Parcels_lyr,LONGITUDE,-1,-1;\
                               TYPE_CODE "TYPE_CODE" true true false 3 Text 0 0 ,First,#,Parcels_lyr,TYPE_CODE,-1,-1;\
                               PCL_CITY "PCL_CITY" true true false 50 Text 0 0 ,First,#,Parcels_lyr,PCL_CITY,-1,-1;\
                               LAND_USE_T "LAND_USE_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,LAND_USE_T,-1,-1;\
                               LAND_USE "LAND_USE" true true false 10 Text 0 0 ,First,#,Parcels_lyr,LAND_USE,-1,-1;\
                               M_HOME_IND "M_HOME_IND" true true false 1 Text 0 0 ,First,#,Parcels_lyr,M_HOME_IND,-1,-1;\
                               ZONING "ZONING" true true false 15 Text 0 0 ,First,#,Parcels_lyr,ZONING,-1,-1;\
                               PROP_IND_T "PROP_IND_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,PROP_IND_T,-1,-1;\
                               PROP_IND "PROP_IND" true true false 3 Text 0 0 ,First,#,Parcels_lyr,PROP_IND,-1,-1;\
                               SUB_TR_NUM "SUB_TR_NUM" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SUB_TR_NUM,-1,-1;\
                               SUB_PLT_BK "SUB_PLT_BK" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SUB_PLT_BK,-1,-1;\
                               SUB_PLT_PG "SUB_PLT_PG" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SUB_PLT_PG,-1,-1;\
                               SUB_NAME "SUB_NAME" true true false 60 Text 0 0 ,First,#,Parcels_lyr,SUB_NAME,-1,-1;\
                               SITE_NBRPX "SITE_NBRPX" true true false 5 Text 0 0 ,First,#,Parcels_lyr,SITE_NBRPX,-1,-1;\
                               SITE_NBR "SITE_NBR" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SITE_NBR,-1,-1;\
                               SITE_NBR2 "SITE_NBR2" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SITE_NBR2,-1,-1;\
                               SITE_NBRSX "SITE_NBRSX" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SITE_NBRSX,-1,-1;\
                               SITE_DIR "SITE_DIR" true true false 2 Text 0 0 ,First,#,Parcels_lyr,SITE_DIR,-1,-1;\
                               SITE_STR "SITE_STR" true true false 30 Text 0 0 ,First,#,Parcels_lyr,SITE_STR,-1,-1;\
                               SITE_MODE "SITE_MODE" true true false 5 Text 0 0 ,First,#,Parcels_lyr,SITE_MODE,-1,-1;\
                               SITE_QDRT "SITE_QDRT" true true false 2 Text 0 0 ,First,#,Parcels_lyr,SITE_QDRT,-1,-1;\
                               SITE_UNIT "SITE_UNIT" true true false 10 Text 0 0 ,First,#,Parcels_lyr,SITE_UNIT,-1,-1;\
                               SITE_CITY "SITE_CITY" true true false 40 Text 0 0 ,First,#,Parcels_lyr,SITE_CITY,-1,-1;\
                               SITE_STATE "SITE_STATE" true true false 2 Text 0 0 ,First,#,Parcels_lyr,SITE_STATE,-1,-1;\
                               SITE_ZIP "SITE_ZIP" true true false 9 Text 0 0 ,First,#,Parcels_lyr,SITE_ZIP,-1,-1;\
                               SITE_CC "SITE_CC" true true false 4 Text 0 0 ,First,#,Parcels_lyr,SITE_CC,-1,-1;\
                               SITE_IND "SITE_IND" true true false 1 Text 0 0 ,First,#,Parcels_lyr,SITE_IND,-1,-1;\
                               MAIL_NBRPX "MAIL_NBRPX" true true false 5 Text 0 0 ,First,#,Parcels_lyr,MAIL_NBRPX,-1,-1;\
                               MAIL_NBR "MAIL_NBR" true true false 10 Text 0 0 ,First,#,Parcels_lyr,MAIL_NBR,-1,-1;\
                               MAIL_NBR2 "MAIL_NBR2" true true false 10 Text 0 0 ,First,#,Parcels_lyr,MAIL_NBR2,-1,-1;\
                               MAIL_NBRSX "MAIL_NBRSX" true true false 10 Text 0 0 ,First,#,Parcels_lyr,MAIL_NBRSX,-1,-1;\
                               MAIL_DIR "MAIL_DIR" true true false 2 Text 0 0 ,First,#,Parcels_lyr,MAIL_DIR,-1,-1;\
                               MAIL_STR "MAIL_STR" true true false 30 Text 0 0 ,First,#,Parcels_lyr,MAIL_STR,-1,-1;\
                               MAIL_MODE "MAIL_MODE" true true false 5 Text 0 0 ,First,#,Parcels_lyr,MAIL_MODE,-1,-1;\
                               MAIL_QDRT "MAIL_QDRT" true true false 2 Text 0 0 ,First,#,Parcels_lyr,MAIL_QDRT,-1,-1;\
                               MAIL_UNIT "MAIL_UNIT" true true false 10 Text 0 0 ,First,#,Parcels_lyr,MAIL_UNIT,-1,-1;\
                               MAIL_CITY "MAIL_CITY" true true false 40 Text 0 0 ,First,#,Parcels_lyr,MAIL_CITY,-1,-1;\
                               MAIL_STATE "MAIL_STATE" true true false 2 Text 0 0 ,First,#,Parcels_lyr,MAIL_STATE,-1,-1;\
                               MAIL_ZIP "MAIL_ZIP" true true false 9 Text 0 0 ,First,#,Parcels_lyr,MAIL_ZIP,-1,-1;\
                               MAIL_CC "MAIL_CC" true true false 4 Text 0 0 ,First,#,Parcels_lyr,MAIL_CC,-1,-1;\
                               ASSD_VAL "ASSD_VAL" true true false 8 Double 0 0 ,First,#,Parcels_lyr,ASSD_VAL,-1,-1;\
                               ASSD_LAN "ASSD_LAN" true true false 8 Double 0 0 ,First,#,Parcels_lyr,ASSD_LAN,-1,-1;\
                               ASSD_IMP "ASSD_IMP" true true false 8 Double 0 0 ,First,#,Parcels_lyr,ASSD_IMP,-1,-1;\
                               TAX_YR "TAX_YR" true true false 8 Double 0 0 ,First,#,Parcels_lyr,TAX_YR,-1,-1;\
                               ASSD_YR "ASSD_YR" true true false 8 Double 0 0 ,First,#,Parcels_lyr,ASSD_YR,-1,-1;\
                               SALE_DT "SALE_DT" true true false 8 Double 0 0 ,First,#,Parcels_lyr,SALE_DT,-1,-1;\
                               SALE_PRICE "SALE_PRICE" true true false 8 Double 0 0 ,First,#,Parcels_lyr,SALE_PRICE,-1,-1;\
                               SALE_TYP_T "SALE_TYP_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,SALE_TYP_T,-1,-1;\
                               SALE_TYP "SALE_TYP" true true false 4 Text 0 0 ,First,#,Parcels_lyr,SALE_TYP,-1,-1;\
                               LAND_ACRES "LAND_ACRES" true true false 8 Double 0 0 ,First,#,Parcels_lyr,LAND_ACRES,-1,-1;\
                               LAND_SQ_FT "LAND_SQ_FT" true true false 8 Double 0 0 ,First,#,Parcels_lyr,LAND_SQ_FT,-1,-1;\
                               GR_SQ_FT "GR_SQ_FT" true true false 8 Double 0 0 ,First,#,Parcels_lyr,GR_SQ_FT,-1,-1;\
                               BSMT_SQ_FT "BSMT_SQ_FT" true true false 8 Double 0 0 ,First,#,Parcels_lyr,BSMT_SQ_FT,-1,-1;\
                               YR_BLT "YR_BLT" true true false 8 Double 0 0 ,First,#,Parcels_lyr,YR_BLT,-1,-1;\
                               BEDROOMS "BEDROOMS" true true false 8 Double 0 0 ,First,#,Parcels_lyr,BEDROOMS,-1,-1;\
                               BSMT_FNS_T "BSMT_FNS_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,BSMT_FNS_T,-1,-1;\
                               BSMT_FNSH "BSMT_FNSH" true true false 3 Text 0 0 ,First,#,Parcels_lyr,BSMT_FNSH,-1,-1;\
                               CONS_TYP_T "CONS_TYP_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,CONS_TYP_T,-1,-1;\
                               CONSTR_TYP "CONSTR_TYP" true true false 3 Text 0 0 ,First,#,Parcels_lyr,CONSTR_TYP,-1,-1;\
                               EXT_WALL_T "EXT_WALL_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,EXT_WALL_T,-1,-1;\
                               EXT_WALLS "EXT_WALLS" true true false 3 Text 0 0 ,First,#,Parcels_lyr,EXT_WALLS,-1,-1;\
                               FOUND_T "FOUND_T" true true false 30 Text 0 0 ,First,#,Parcels_lyr,FOUND_T,-1,-1;\
                               FOUNDATION "FOUNDATION" true true false 3 Text 0 0 ,First,#,Parcels_lyr,FOUNDATION,-1,-1;\
                               STORY_NBR "STORY_NBR" true true false 8 Double 0 0 ,First,#,Parcels_lyr,STORY_NBR,-1,-1;\
                               BLD_UNITS "BLD_UNITS" true true false 8 Double 0 0 ,First,#,Parcels_lyr,BLD_UNITS,-1,-1;\
                               UNITS_NBR "UNITS_NBR" true true false 8 Double 0 0 ,First,#,Parcels_lyr,UNITS_NBR,-1,-1;\
                               VINTAGE "VINTAGE" true true false 8 Date 0 0 ,First,#,Parcels_lyr,VINTAGE,-1,-1;\
                               MI "MI" true true false 8 Double 0 0 ,First,#,Parcels_lyr,MI,-1,-1;\
                               MI_int "MI_int" true true false 4 Long 0 0 ,First,#,Parcels_lyr,MI_int,-1,-1;\
                               PGA "PGA" true true false 8 Double 0 0 ,First,#,Parcels_lyr,PGA,-1,-1;\
                               PGV "PGV" true true false 8 Double 0 0 ,First,#,Parcels_lyr,PGV,-1,-1;\
                               svi_total "svi_total" true true false 4 Long 0 0 ,First,#,SVI_lyr,F_TOTAL,-1,-1', "INTERSECT", "", "")


# Calculate Weight for Heat Map (MI + SVI)
arcpy.AddField_management(Parcels_SVI, "TOTAL", "DOUBLE")
#arcpy.CalculateField_management(Parcels_SVI, "TOTAL", "[F_TOTAL]+ 2*[MI]", "VB", "")
arcpy.CalculateField_management(Parcels_SVI, "TOTAL", "[svi_total]+ 2*[MI]", "VB", "")

arcpy.MakeFeatureLayer_management(Parcels_SVI, "Parcels_SVI_lyr")
arcpy.SelectLayerByAttribute_management("Parcels_SVI_lyr", "NEW_SELECTION", "MI_int >=6")

#KERNEL DENSITY
#arcpy.gp.KernelDensity_sa("Parcels_SVI_lyr", "TOTAL", GDB+"\\HazardExposureMap", "", "", "SQUARE_MAP_UNITS", "DENSITIES", "PLANAR")
arcpy.gp.KernelDensity_sa("Parcels_SVI_lyr", "TOTAL", GDB+"\\HazardExposureMap", 0.000716, 0.0032, "SQUARE_METERS", "DENSITIES", "PLANAR")





    


