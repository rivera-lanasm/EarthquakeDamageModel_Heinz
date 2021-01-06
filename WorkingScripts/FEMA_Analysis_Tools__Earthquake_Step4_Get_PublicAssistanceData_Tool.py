#-------------------------------------------------------------------------------
# Name:        Get Public Assistance Elements Tool
# Author:      Madeline Jones
# Created:     08/14/2017
#-------------------------------------------------------------------------------




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
pgv = "{}\pgv.shp".format(ShakeMapDir)
pga = "{}\pga.shp".format(ShakeMapDir)

Boolean_Highways = arcpy.GetParameterAsText(2)
Boolean_Bridges = arcpy.GetParameterAsText(3)
Boolean_Ports= arcpy.GetParameterAsText(4)
Boolean_Airports = arcpy.GetParameterAsText(5)
Boolean_Railroads= arcpy.GetParameterAsText(6)
Boolean_RailroadStations= arcpy.GetParameterAsText(7)
Boolean_Levees = arcpy.GetParameterAsText(8)
Boolean_Dams = arcpy.GetParameterAsText(9)
Boolean_Canals = arcpy.GetParameterAsText(10)
Boolean_privateSchools  = arcpy.GetParameterAsText(11)
Boolean_publicSchools  = arcpy.GetParameterAsText(12)
Boolean_Universities  = arcpy.GetParameterAsText(13)
Boolean_stateGovtBldgs = arcpy.GetParameterAsText(14)
Boolean_lawEnforcement= arcpy.GetParameterAsText(15)
Boolean_Prisons= arcpy.GetParameterAsText(16)
Boolean_Hospitals= arcpy.GetParameterAsText(17)
Boolean_UrgentCare = arcpy.GetParameterAsText(18)
Boolean_NursingHomes  = arcpy.GetParameterAsText(19)
Boolean_DayCareCenters= arcpy.GetParameterAsText(20)
Boolean_LocalEOCs= arcpy.GetParameterAsText(21)
Boolean_StateEOCs= arcpy.GetParameterAsText(22)
Boolean_wasteWaterTreatment = arcpy.GetParameterAsText(23)
Boolean_SolidWasteLandfillFacs = arcpy.GetParameterAsText(24)
Boolean_ChemicalMfgFacs = arcpy.GetParameterAsText(25)
Boolean_powerPlants= arcpy.GetParameterAsText(26)
Boolean_NuclearPowerPlants= arcpy.GetParameterAsText(27)
Boolean_naturalGasPipelines = arcpy.GetParameterAsText(28)
Boolean_naturalGasProcessingPlant = arcpy.GetParameterAsText(29)
Boolean_naturalGasStorageFacility = arcpy.GetParameterAsText(30)
Boolean_OilRefineries = arcpy.GetParameterAsText(31)
Boolean_powerLines= arcpy.GetParameterAsText(32)
Boolean_cellTowers  = arcpy.GetParameterAsText(33)
Boolean_electricSubstations= arcpy.GetParameterAsText(34)
Boolean_parks = arcpy.GetParameterAsText(35)
Boolean_piers  = arcpy.GetParameterAsText(36)
Boolean_massTransit = arcpy.GetParameterAsText(37)
Boolean_fireStations = arcpy.GetParameterAsText(38)
Boolean_DODsiteBldgFootprints = arcpy.GetParameterAsText(39)
Boolean_DODsiteLocations = arcpy.GetParameterAsText(40)
Boolean_Pharmacies = arcpy.GetParameterAsText(41)
#Boolean_GroceryStores = arcpy.GetParameterAsText(42)
#Boolean_PSAP = arcpy.GetParameterAsText(43)


def finish(arg=None):
    try:
        sys.exit(arg)
    except SystemExit:
        pass



arcpy.MakeFeatureLayer_management(mi,"mi_lyr")
arcpy.MakeFeatureLayer_management(pgv,"pgv_lyr")
arcpy.MakeFeatureLayer_management(pga,"pga_lyr")


    

def intersect_feature_w_hazard(feature, name, fcName, Category):
    
    arcpy.MakeFeatureLayer_management(feature,"{}_lyr".format(feature))
    INTs = arcpy.SelectLayerByLocation_management("{}_lyr".format(feature),"INTERSECT","mi_lyr","","NEW_SELECTION")
    Count = int(arcpy.GetCount_management(INTs)[0])

    if Count > 0:
        arcpy.AddMessage("{} {} intersect with ShakeMap layer. Copying to workspace.".format(Count, name))
        arcpy.CopyFeatures_management(INTs, fcName)
        arcpy.AddField_management(fcName, "PA_Type", "TEXT")
        arcpy.AddField_management(fcName, "PA_Category", "TEXT")
        arcpy.CalculateField_management(fcName, "PA_Type", '"{}"'.format(name), "VB", "")
        arcpy.CalculateField_management(fcName, "PA_Category", '"{}"'.format(Category), "VB", "")
    else:
        arcpy.AddMessage("0 {} intersect with ShakeMap layer.".format(name))

    return 



#Category C: Roads, Bridges

if str(Boolean_Highways) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Highways (Category C).")
    highways = r"\\hqmac3f1\Static\GISdata\ESRI\2016\usa\trans\highways.gdb\highways"
    intersect_feature_w_hazard(highways, "Highways", "PA_Highways", "C")

if str(Boolean_Bridges) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Bridges (Category C).")
    bridges = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Transportation_Ground\National_Bridge_Inventory\National_Bridge_Inventory_NBI_Bridges.shp"
    intersect_feature_w_hazard(bridges, "Bridges", "PA_Bridges", "C")

if str(Boolean_Ports) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Ports (Category C).")
    Ports = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\TransWater\TransWater.gdb\PortFacs"
    intersect_feature_w_hazard(Ports, "Ports", "PA_Ports", "C")

if str(Boolean_Airports) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Airports (Category C).")
    Airports = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\TransAir\TransAir.gdb\AirportBndrys"
    intersect_feature_w_hazard(Airports, "Airports", "PA_Airports", "C")

if str(Boolean_Railroads) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Railroads (Category C).")
    Railroads = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\TransGround\TransGround.gdb\Railroads"
    intersect_feature_w_hazard(Railroads, "Railroads", "PA_Railroads", "C")

if str(Boolean_RailroadStations) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Railroad Stations (Category C).")
    RailroadStations = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\TransGround\TransGround.gdb\RailroadStations"
    intersect_feature_w_hazard(RailroadStations, "Railroad Stations", "PA_RailroadStations", "C")


#Category D: Water Control Facilities

if str(Boolean_Levees) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Levees (Category D).")
    levees = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\National_Levee_Dataset\NationalLeveeDataset_LeveeCenterlines.shp"
    intersect_feature_w_hazard(levees, "Levees", "PA_Levees", "D")

if str(Boolean_Dams) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Dams (Category D).")
    dams = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\WaterSupply\WaterSupply.gdb\DamLines"
    intersect_feature_w_hazard(dams, "Dams", "PA_Dams", "D")
    
if str(Boolean_Canals) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Canals (Category D).")
    canals = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Transportation_Water\Canals\NHD_Canals.shp"
    intersect_feature_w_hazard(canals, "Canals", "PA_Canals", "D")





#Category E: Buildings & Equipment


if str(Boolean_privateSchools) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Private Schools (Category E).")
    privateSchools = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Education\Private_Schools\Private_Schools.shp"
    intersect_feature_w_hazard(privateSchools, "Private Schools", "PA_PrivateSchools", "E")

if str(Boolean_publicSchools) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Public Schools (Category E).")
    publicSchools = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Education\Public_Schools\Public_Schools.shp"
    intersect_feature_w_hazard(publicSchools, "Public Schools", "PA_PublicSchools", "E")

if str(Boolean_Universities) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Universities (Category E).")
    universities = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Education\Colleges_And_Universities\Colleges_and_Universities.shp"
    intersect_feature_w_hazard(universities, "Colleges and Universities", "PA_Colleges_and_Universities", "E")
   
if str(Boolean_stateGovtBldgs) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Government Buildings (Category E).")
    stateGovtBldgs = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Government\Major_State_Government_Buildings\Major_State_Government_Buildings.shp"
    intersect_feature_w_hazard(stateGovtBldgs, "Major State Government Buildings", "PA_MajorStateGovernmentBuildings", "E")

if str(Boolean_lawEnforcement) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Law Enforcement Buildings (Category E).")
    lawEnforcement = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Law_Enforcement\Local_Law_Enforcement_Locations\Local_Law_Enforcement_Locations.shp"
    intersect_feature_w_hazard(lawEnforcement, "Law Enforcement Buildings", "PA_LawEnforcement", "E")

if str(Boolean_Prisons) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Prisons (Category E).")
    Prisons = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Law_Enforcement\Prison_Boundaries\Prison_Boundaries.shp"
    intersect_feature_w_hazard(Prisons, "Prisons", "PA_Prisons", "E")
    
if str(Boolean_Hospitals) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Hospitals (Category E).")
    Hospitals = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Public_Health\Hospitals\Hospitals.shp"
    intersect_feature_w_hazard(Hospitals, "Hospitals", "PA_Hospitals", "E")

if str(Boolean_UrgentCare) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Urgent Care Facilities (Category E).")
    UrgentCare = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Public_Health\Urgent_Care_Facilities\Urgent_Care_Facilities.shp"
    intersect_feature_w_hazard(UrgentCare, "Urgent Care Facilities", "PA_UrgentCare", "E")

if str(Boolean_NursingHomes) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Nursing Homes (Category E).")
    NursingHomes = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Public_Health\Nursing_Homes\Nursing_Homes.shp"
    intersect_feature_w_hazard(NursingHomes, "Nursing Homes", "PA_NursingHomes", "E")

if str(Boolean_Pharmacies) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Pharmacies (Category E).")
    Pharmacies = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Public_Health\Pharmacies\Pharmacies.shp"
    intersect_feature_w_hazard(Pharmacies, "Pharmacies", "PA_Pharmacies", "E")

if str(Boolean_DayCareCenters) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Day Care Centers (Category E).")
    DayCareCenters = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Education\Day_Care_Centers\Day_Care_Centers.shp"
    intersect_feature_w_hazard(DayCareCenters, "Day Care Centers", "PA_DayCareCenters", "E")
    
if str(Boolean_LocalEOCs) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Local EOCs (Category E).")
    LocalEOCs = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Emergency_Services\Local_Emergency_Operations_Centers_EOC\Local_Emergency_Operations_Centers_EOC.shp"
    intersect_feature_w_hazard(LocalEOCs, "Local EOC's", "PA_LocalEOC", "E")

if str(Boolean_StateEOCs) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with State EOCs (Category E).")
    StateEOCs = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Emergency_Services\State_Emergency_Operations_Centers_EOC\State_Emergency_Operations_Centers_EOC.shp"
    intersect_feature_w_hazard(StateEOCs, "State EOC's", "PA_StateEOC", "E")

if str(Boolean_DODsiteBldgFootprints) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with DoD Site Building Footprints (Category E).")
    DoDFootprints = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Government\Government.gdb\DoD_SiteBuildingFootprints"
    intersect_feature_w_hazard(DoDFootprints, "DoD Site Building Footprints", "PA_DoDsiteBldgFootprints", "E")

if str(Boolean_DODsiteLocations) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with DoD Site Locations (Category E).")
    DoDSites = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Government\Government.gdb\DoD_SiteLocs"
    intersect_feature_w_hazard(DoDSites, "DoD Site Locations", "PA_DoDsiteLocations", "E")

#Category F: Utilities


if str(Boolean_wasteWaterTreatment) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Waste Water Treatment Facilities (Category F).")
    wasteWaterTreatment = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Water_Supply\Environmental_Protection_Agency_EPA_Facility_Registry_Service_FRS_Wastewater_Treatment_Plants\Environmental_Protection_Agency_EPA_Facility_Registry_Service_FRS_Wastewater_Treatment_Plants.shp"
    intersect_feature_w_hazard(wasteWaterTreatment, "Waste Water Treatment Plants", "PA_WasteWaterTreatment", "F")

if str(Boolean_SolidWasteLandfillFacs) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Solid Waste Landfill Facilities (Category F).")
    SolidWasteLandfillFacs = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Chemicals\Chemical.gdb\SolidWasteLandfillFacs"
    intersect_feature_w_hazard(SolidWasteLandfillFacs, "Solid Waste Landfill Facilities", "PA_SolidWasteLandfillFacilities", "F")

if str(Boolean_ChemicalMfgFacs) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Chemical Manufacturing Facilities (Category F).")
    ChemicalMfgFacs = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Chemicals\Chemical.gdb\ChemicalMfgFacs"
    intersect_feature_w_hazard(ChemicalMfgFacs, "Chemical Manufacturing Facilities", "PA_ChemicalManufacturing", "F")

if str(Boolean_powerPlants) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Power Plants (Category F).")
    powerPlants = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Energy\Power_Plants\Power_Plants.shp"
    intersect_feature_w_hazard(powerPlants, "Power Plants", "PA_PowerPlants", "F")

if str(Boolean_NuclearPowerPlants) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Nuclear Power Plants (Category F).")
    NuclearPowerPlants = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Energy\Energy.gdb\NuclearPowerPlants"
    intersect_feature_w_hazard(NuclearPowerPlants, "Nuclear Power Plants", "PA_NuclearPowerPlants", "F")

if str(Boolean_naturalGasPipelines) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Natural Gas Pipelines (Category F).")
    naturalGasPipelines = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Energy\Natural_Gas_Liquid_Pipelines\Natural_Gas_Liquid_Pipelines.shp"
    intersect_feature_w_hazard(naturalGasPipelines, "Natural Gas Pipelines", "PA_NaturalGasPipelines", "F")

if str(Boolean_naturalGasProcessingPlant) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Natural Gas Processing Plants (Category F).")
    naturalGasProcessingPlant = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Energy\Energy.gdb\NaturalGasProcessingPlants"
    intersect_feature_w_hazard(naturalGasProcessingPlant, "Natural Gas Processing Plants", "PA_NaturalGasProcessingPlants", "F")

if str(Boolean_naturalGasStorageFacility) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Natural Gas Storage Facilities (Category F).")
    naturalGasStorageFacility = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Energy\Energy.gdb\NaturalGasStorageFacs"
    intersect_feature_w_hazard(naturalGasStorageFacility, "Natural Gas Storage Facilities", "PA_NaturalGasStorageFacilities", "F")

if str(Boolean_OilRefineries) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Oil Refineries (Category F).")
    OilRefineries = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\Energy\Energy.gdb\OilRefineries"
    intersect_feature_w_hazard(OilRefineries, "Oil Refineries", "PA_OilRefineries", "F")
    

if str(Boolean_powerLines) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Power Lines (Category F).")
    powerLines = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Energy\Electric_Power_Transmission_Lines\Electric_Power_Transmission_Lines.shp"
    intersect_feature_w_hazard(powerLines, "Power Lines", "PA_PowerLines", "F")

if str(Boolean_cellTowers) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Cell Towers (Category F).")
    cellTowers = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Communications\Cellular_Towers\Cellular_Towers.shp"
    intersect_feature_w_hazard(cellTowers, "Cell Towers", "PA_CellTowers", "F")

if str(Boolean_electricSubstations) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Electric Substations (Category F).")
    electricSubstations = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Energy\Electric_Substations\Electric_Substations.shp"
    intersect_feature_w_hazard(electricSubstations, "Electric Substations", "PA_ElectricSubstations", "F")




#Category G: Parks, Recreational Areas, Other


if str(Boolean_parks) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Parks (Category G).")
    parks = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_1_Infrastruture\PubVenues\PubVenues.gdb\StateCountyLocalParksBndrys"
    intersect_feature_w_hazard(parks, "Parks", "PA_Parks", "F")
    
if str(Boolean_piers) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Piers (Category G).")
    piers = r"\\hqmac3f1\Static\GISdata\HSIP_DATA\HSIP_2015\DISC_2_Infrastruture\TransWater\TransWater.gdb\PiersWharvesQuays"
    intersect_feature_w_hazard(piers, "Piers", "PA_Piers", "F")

if str(Boolean_massTransit) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Public Transit Stations (Category G).")
    massTransit = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Transportation_Ground\Public_Transit_Stations\Public_Transit_Stations.shp"
    intersect_feature_w_hazard(massTransit, "Public Transit Stations", "PA_PublicTransitStations", "F")




#Category H: Fire Management

if str(Boolean_fireStations) == 'true':
    arcpy.AddMessage("Intersecting ShakeMap layer with Fire Stations (Category H).")
    fireStations = r"\\hqmac3f1\Static\GISdata\HIFLD_DATA_2016\HIFLD_OPEN\Emergency_Services\FireStations\FireStations.shp"
    intersect_feature_w_hazard(fireStations, "Fire Stations", "PA_FireStations", "H")


arcpy.AddMessage("Adding MMI, PGA, and PGV data to PA attribute tables.")

## ADD MI, PGA, PGV TO PA ATTRIBUTE TABLES



PA_list = arcpy.ListFeatureClasses("PA_*")
for PA in PA_list:
    arcpy.MakeFeatureLayer_management(PA, PA+"_lyr")
    arcpy.SpatialJoin_analysis(PA+"_lyr", "mi_lyr", PA+"_MI", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
    arcpy.AlterField_management(PA+"_MI", "PARAMVALUE", "MI", "MI", "DOUBLE", "8", "NULLABLE", "false")
    arcpy.DeleteField_management(PA+"_MI", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
    arcpy.Delete_management(GDB + "\\"+PA)

PA_list = arcpy.ListFeatureClasses("PA_*_MI")
for PA in PA_list:
    arcpy.MakeFeatureLayer_management(PA, PA+"_lyr")
    arcpy.SpatialJoin_analysis(PA+"_lyr", "pga_lyr", PA+"_PGA", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
    arcpy.AlterField_management(PA+"_PGA", "PARAMVALUE", "PGA", "PGA", "DOUBLE", "8", "NULLABLE", "false")
    arcpy.DeleteField_management(PA+"_PGA", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
    arcpy.Delete_management(GDB + "\\"+PA)

PA_list = arcpy.ListFeatureClasses("PA_*_PGA")
for PA in PA_list:
    arcpy.MakeFeatureLayer_management(PA, PA+"_lyr")
    arcpy.SpatialJoin_analysis(PA+"_lyr", "pgv_lyr", PA[:-7], "JOIN_ONE_TO_ONE", "KEEP_ALL","")
    arcpy.AlterField_management(PA[:-7], "PARAMVALUE", "PGV", "PGV", "DOUBLE", "8", "NULLABLE", "false")
    arcpy.DeleteField_management(PA[:-7], "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
    arcpy.Delete_management(GDB + "\\"+PA)

PA_list = arcpy.ListFeatureClasses("PA_*")
for PA in PA_list:
    arcpy.AddField_management(PA, "MI_INT", "SHORT", "", "", "", "MI_int")
    arcpy.CalculateField_management(PA, "MI_INT", "math.floor( !MI! )", "PYTHON_9.3", "")
                              
#PA_list = arcpy.ListFeatureClasses("PA_*")
#for PA in PA_list:
#    arcpy.AddField_management(PA, "STATUS", "TEXT")
#    arcpy.CalculateField_management(PA, "STATUS", "Unknown")

arcpy.AddMessage("PA analysis complete.")
    
