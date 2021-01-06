import arcpy
import math
import os
import sys
import json
import shutil
import datetime
import time

arcpy.env.workspace = arcpy.GetParameterAsText(0)
GDB = arcpy.env.workspace

arcpy.env.overwriteOutput = True

Parcels = arcpy.GetParameterAsText(1)
Counties = arcpy.GetParameterAsText(2)
MI = arcpy.GetParameterAsText(3)


arcpy.MakeFeatureLayer_management(MI,"MI_lyr")
arcpy.MakeFeatureLayer_management(Parcels,"Parcels_lyr")
arcpy.MakeFeatureLayer_management(Counties,"Counties_lyr")

# Get Max MI 
maxlist=[]
cursor = arcpy.da.SearchCursor(MI, "MI_int")
for row in cursor:
    maxlist.append(row[0])
MaxMI = max(maxlist)

# GET PARCEL COUNTS PER MI
arcpy.AddField_management("MI_lyr","Parcel_Count","LONG")
arcpy.CalculateField_management(MI,"Parcel_Count",0)

x = 1
while x <= MaxMI:
    Selection = arcpy.SelectLayerByAttribute_management("MI_lyr","NEW_SELECTION","MI_int = {}".format(x))
    SelectionCount = arcpy.GetCount_management(Selection)[0]
    if int(SelectionCount) > 0:
        Selection2 = arcpy.SelectLayerByLocation_management("Parcels_lyr","INTERSECT",Selection,"","NEW_SELECTION","")
        NumParcels = arcpy.GetCount_management(Selection2)[0]
        arcpy.CalculateField_management(Selection,"Parcel_Count","{}".format(NumParcels))
        arcpy.AddMessage('{} parcels within MI {}'.format(NumParcels, x))
    x = x + 1


# GET PA COUNTS PER MI
PAlist = []
PAlist_full = arcpy.ListFeatureClasses("PA_*")
for PA in PAlist_full:
    PAlist.append(PA[3:])

for PA in PAlist:
    arcpy.AddField_management(MI,PA+"_Count","LONG")
    arcpy.MakeFeatureLayer_management("PA_"+PA, PA+"_lyr")
    x = 1
    while x <= MaxMI:
        Selection = arcpy.SelectLayerByAttribute_management("MI_lyr","NEW_SELECTION","MI_int = {}".format(x))
        SelectionCount = arcpy.GetCount_management(Selection)[0]
        if int(SelectionCount) > 0:
            Selection2 = arcpy.SelectLayerByLocation_management(PA+"_lyr","INTERSECT",Selection,"","NEW_SELECTION","")
            Num = arcpy.GetCount_management(Selection2)[0]
            arcpy.CalculateField_management(Selection,PA+"_Count","{}".format(Num))
            arcpy.AddMessage('{} {} within MI {}'.format(Num, PA, x))
        x = x + 1


# Add Fields to Counties
x = 1
while x <= MaxMI:
    arcpy.AddField_management(Counties,"Parcel_Count_MI{}".format(x),"LONG")
    arcpy.CalculateField_management(Counties,"Parcel_Count_MI{}".format(x),0)
    x = x+1

# Get Parcel Count Per MI Per County
FIPSlist=[]
cursor = arcpy.da.SearchCursor(Counties, "FIPS")
for row in cursor:
    FIPSlist.append(row[0])
    
for FIPSs in FIPSlist:
    arcpy.AddMessage('Counting Parcels in County FIPS {}'.format(FIPSs))
    SelectedCounty = arcpy.SelectLayerByAttribute_management("Counties_lyr","NEW_SELECTION","FIPS = '{}'".format(FIPSs))
    Selection2 = arcpy.SelectLayerByLocation_management("Parcels_lyr","INTERSECT",SelectedCounty,"","NEW_SELECTION","")
    NumP = arcpy.GetCount_management(Selection2)[0]
    if int(NumP) > 0:
        # Get Min/Max MI of Parcels
        maxlist=[]
        cursor = arcpy.da.SearchCursor(Selection2, "MI_int")
        for row in cursor:
            maxlist.append(row[0])
        MaxMIp = max(maxlist)
        MinMIp = min(maxlist)

        y = MinMIp
        while y <= MaxMIp:
            Selection2 = arcpy.SelectLayerByLocation_management("Parcels_lyr","INTERSECT",SelectedCounty,"","NEW_SELECTION","")
            Selection3 = arcpy.SelectLayerByAttribute_management(Selection2,"SUBSET_SELECTION","MI_int={}".format(y))
            NumF = arcpy.GetCount_management(Selection3)[0]
            arcpy.CalculateField_management(SelectedCounty,"Parcel_Count_MI{}".format(y),"{}".format(NumF))
            y = y+1


# Get PA Count Per MI Per County
for PA in PAlist:
    x = 1
    while x <= MaxMI:
        arcpy.AddField_management(Counties,PA+"_Count_MI{}".format(x),"LONG")
        arcpy.CalculateField_management(Counties,PA+"_Count_MI{}".format(x),0)
        x = x+1
    for FIPSs in FIPSlist:
        arcpy.AddMessage('Counting {} in County FIPS {}'.format(PA, FIPSs))
        SelectedCounty = arcpy.SelectLayerByAttribute_management("Counties_lyr","NEW_SELECTION","FIPS = '{}'".format(FIPSs))
        Selection2 = arcpy.SelectLayerByLocation_management(PA+"_lyr","INTERSECT",SelectedCounty,"","NEW_SELECTION","")
        NumA = arcpy.GetCount_management(Selection2)[0]
        if int(NumA) > 0:
            # Get Min/Max MI of PA
            maxlist=[]
            cursor = arcpy.da.SearchCursor(Selection2, "MI_int")
            for row in cursor:
                maxlist.append(row[0])
            MaxMIa = max(maxlist)
            MinMIa = min(maxlist)

            y = MinMIa
            while y <= MaxMIa:
                Selection2 = arcpy.SelectLayerByLocation_management(PA+"_lyr","INTERSECT",SelectedCounty,"","NEW_SELECTION","")
                Selection3 = arcpy.SelectLayerByAttribute_management(Selection2,"SUBSET_SELECTION","MI_int={}".format(y))
                NumB = arcpy.GetCount_management(Selection3)[0]
                arcpy.CalculateField_management(SelectedCounty,PA+"_Count_MI{}".format(y),"{}".format(NumB))
                y = y+1


    



