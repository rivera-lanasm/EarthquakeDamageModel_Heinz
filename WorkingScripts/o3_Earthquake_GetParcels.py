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
    GDB = arcpy.env.workspace

    #get list of intersecting states
    state_names_list = unique_values(table=os.path.join(GDB, "census_county_max_mmi_pga_pgv"), field="STATE_NAME")

    bldgs_output = os.path.join(GDB, "ORNL_LB_bldgs")

    #select building centroids that are within intersecting states and intersect them with shakemap
    for state in state_names_list:
        arcpy.management.MakeFeatureLayer(os.path.join(bldg_gdb, state), "{}_lyr".format(state))
        arcpy.management.SelectLayerByLocation("{}_lyr".format(state), 'INTERSECT', "shakemap_countyclip_mmi")
    if len(state_names_list) > 1:
        #merge
        arcpy.Merge_management(["{}_lyr".format(x) for x in state_names_list], bldgs_output)
    else:
        #copy features
        arcpy.CopyFeatures_management("{}_lyr".format(state), bldgs_output)

    return bldgs_output



PointsManifest = r"\\hqmac3f1\Static\GISdata\Parcel_Data\CL_16MAY2017\Support\points_manifest.dbf"
CountyIndexLayer = r"\\hqmac3f1\Static\GISdata\Census\TIGER Shapefiles\2016\Counties\tl_2016_us_county_WGS84.shp"
StateList = {
    "AL" : "Alabama",
    "AK" : "Alaska",
    "AZ" : "Arizona",
    "AR" : "Arkansas",
    "CA" : "California",
    "CO" : "Colorado",
    "CT" : "Connecticut",
    "DE" : "Delaware",
    "DC" : "District_Of_Columbia",
    "FL" : "Florida",
    "GA" : "Georgia",
    "HI" : "Hawaii",
    "ID" : "Idaho",
    "IL" : "Illinois",
    "IN" : "Indiana",
    "IA" : "Iowa",
    "KS" : "Kansas",
    "KY" : "Kentucky",
    "LA" : "Louisiana",
    "ME" : "Maine",
    "MD" : "Maryland",
    "MA" : "Massachusetts",
    "MI" : "Michigan",
    "MN" : "Minnesota",
    "MS" : "Mississippi",
    "MO" : "Missouri",
    "MT" : "Montana",
    "NE" : "Nebraska",
    "NV" : "Nevada",
    "NH" : "New_Hampshire",
    "NJ" : "New_Jersey",
    "NM" : "New_Mexico",
    "NY" : "New_York",
    "NC" : "North_Carolina",
    "ND" : "North_Dakota",
    "OH" : "Ohio",
    "OK" : "Oklahoma",
    "OR" : "Oregon",
    "PA" : "Pennsylvania",
    "RI" : "Rhode_Island",
    "SC" : "South_Carolina",
    "SD" : "South_Dakota",
    "TN" : "Tennessee",
    "TX" : "Texas",
    "UT" : "Utah",
    "VT" : "Vermont",
    "VA" : "Virginia",
    "WA" : "Washington",
    "WV" : "West_Virginia",
    "WI" : "Wisconsin",
    "WY" : "Wyoming"
    }







def get_date():
    
    Day = datetime.date.today().strftime("%d")
    Mo = datetime.date.today().strftime("%m")
    Yr = datetime.date.today().strftime("%Y")
    
    DateToday = "{}{}{}".format(Mo,Day,Yr)  # Creates date string in format 'DDMMYYYY'

    return DateToday



class Static:
    
    def __init__(self):
        pass
    
    def get_parcels_for_download(self, CountiesList):
        
        counties = arcpy.SearchCursor(PointsManifest)
        
        ParcelDatasetList = []
        for county in counties:
            Filename = county.Filename
            FIPS = county.FIPS_str
            CountyName = county.Filename[3:-6]

            if FIPS in CountiesList:

                StateAbbrev = Filename.split("_")[0]
           
                if StateAbbrev in StateList:
                    geodb = StateList[StateAbbrev]
     
                    feat_dataset = "{}".format(Filename[:-6])
                    feat_class = Filename
                 
                    ParcelDatasetList.append(r"\\hqmac3f1\Static\GISdata\Parcel_Data\CL_23JULY2018\{}.gdb\{}\{}_Res".format(geodb,feat_dataset,feat_class))
                else:
                    arcpy.AddWarning("State not found for {}...something's wrong.".format(StateAbbrev))
                
        return ParcelDatasetList


    def copy_parcels_by_intersection(self, ParcelDatasetList, layer, Count):
    
        i=0
        for entry in ParcelDatasetList:
            arcpy.MakeFeatureLayer_management(entry, "pointslyr")
            ID = entry.split("\\")[-2]

            ImpactedParcels = arcpy.SelectLayerByLocation_management("pointslyr","INTERSECT",layer,"","NEW_SELECTION")

            if int(arcpy.GetCount_management(ImpactedParcels)[0]) > 0:
                arcpy.CopyFeatures_management(ImpactedParcels,"ParcelPoints_{}".format(ID))
                i=i+1
                Remaining = Count - i
                message = "Parcel data copied to workspace for {}. {} counties remaining.".format(ID, Remaining)
            elif int(arcpy.GetCount_management(ImpactedParcels)[0]) == 0:
                i=i+1
                Remaining = Count - i
                message = "No intersecting parcel data for {}. {} counties remaining.".format(ID, Remaining)

            arcpy.AddMessage(message)
            
        return None

        
    def merge_parcels(self):
        MergeList = arcpy.ListFeatureClasses("ParcelPoints*")
        MergeName = "IA_Parcels"
        arcpy.Merge_management(MergeList,MergeName)

        return MergeName

class AWS:
    bucket = "https://s3.amazonaws.com/fema-parcel-tiles/"
    
    ## uncomment these when inside a FEMA network
    os.environ["HTTP_PROXY"] = "http://proxy.apps.dhs.gov:80"
    os.environ["HTTPS_PROXY"] = "http://proxy.apps.dhs.gov:80"
    os.environ["User_Token"] = "RzVTM19oRTJiZwo="

    def __init__(self):
        pass

    def get_parcels_for_download(self, CountiesList):
        
        counties = arcpy.SearchCursor(PointsManifest)
        
        ParcelDatasetList = []
        for county in counties:
            Filename = county.Filename
            FIPS = county.FIPS_str
            CountyName = county.Filename[3:-6]

            if FIPS in CountiesList:
                
                StateAbbrev = Filename.split("_")[0]
                CountyName = Filename[3:-6]
                
                if StateAbbrev in StateList:
                    Statename = StateList[StateAbbrev]


                    ParcelDatasetList.append("flood/{}/{}_{}.gpkg".format(Statename, StateAbbrev, CountyName))
                
        return ParcelDatasetList


    def retrieve_geopackages(self, fList, bucket):
        tmpFiles = []
        index=0
        for URL in fList:
            file = URL.split("/")[-1]
            
            wrkURL = bucket + URL
            wrkFile = os.path.join(DIR, file)

            if os.path.exists(wrkFile):
                result = "skip Download"
                arcpy.AddMessage("Simulating download for existing geopackage: {}".format(URL))
            else:
                try:
                    result = urlopen(wrkURL)
                except Exception, e:
                    arcpy.AddWarning("Error {}".format(str(e)))
                    arcpy.AddWarning("Failed to load temp geopackage {}.".format(wrkURL))
                    result = None
                    
            if result:
                if not type(result) == str:
                    with open(wrkFile, "wb") as fh:
                      shutil.copyfileobj(result, fh)
                    pass  
                #fh.close()
                tmpFiles.append(wrkFile)
                index = index + 1
                arcpy.AddMessage("Downloaded: {}".format(URL))
                arcpy.AddMessage("{} geopackage downloads remain.".format(len(fList) - index))
            else:
                arcpy.AddWarning("Failed to download {}".format(URL))
                #arcpy.ExecuteError
                #sys.exit()

        return tmpFiles


    def copy_parcels_by_intersection(self, ParcelDatasetList, layer, Count):
    
        NewParcelDatasetList = []
        for entry in ParcelDatasetList:
            newentry = entry + "\\main." + entry.split("\\")[-1].split(".")[0] + "_Point"
            NewParcelDatasetList.append(newentry)
            
        i=0
        for entry in NewParcelDatasetList:
            arcpy.MakeFeatureLayer_management(entry, "pointslyr")
            ID = entry.split("\\")[-2]

            ImpactedParcels = arcpy.SelectLayerByLocation_management("pointslyr","INTERSECT",layer,"","NEW_SELECTION")

            if int(arcpy.GetCount_management(ImpactedParcels)[0]) > 0:
                arcpy.CopyFeatures_management(ImpactedParcels,"ParcelPoints_{}".format(ID[:-5]))
                i=i+1
                Remaining = Count - i
                message = "Parcel data copied to workspace for {}. {} counties remaining.".format(ID[:-5], Remaining)
            elif int(arcpy.GetCount_management(ImpactedParcels)[0]) == 0:
                i=i+1
                Remaining = Count - i
                message = "No intersecting parcel data for {}. {} counties remaining.".format(ID[:-5], Remaining)

            arcpy.AddMessage(message)
            
        return None

    def merge_parcels(self):
        MergeList = arcpy.ListFeatureClasses("ParcelPoints*")
        MergeName = "IA_Parcels"
        arcpy.Merge_management(MergeList, MergeName)

        return MergeName



def scratch_dir():
    DIR = "C:\scratch"
    if not os.path.exists(DIR):
        os.makedirs(DIR)

    return DIR


#if Environment == "AWS":
#    Environ = AWS()
#    DIR = scratch_dir()
#elif Environment == "Static":
#    Environ = Static()
##
##Environment = "AWS"
##Environ = AWS()
##DIR = scratch_dir()

Environment = "Static"
Environ = Static()
DIR = scratch_dir()



def county_intersection(layer):
    
    arcpy.MakeFeatureLayer_management(CountyIndexLayer,"CountyIndexlyr")
    IntersectingCounties = arcpy.SelectLayerByLocation_management("CountyIndexlyr","INTERSECT",layer,"","NEW_SELECTION")
    Count = int(arcpy.GetCount_management(IntersectingCounties)[0])

    return IntersectingCounties, Count


def project_to_WGS1984(feature):
    currentProjection = arcpy.Describe(feature).SpatialReference.name

    if currentProjection == 'GCS_WGS_1984':
        return feature
    
    else:
        projectedFeature = GDB + "\\tempfeature_WGS1984"
        if not arcpy.Exists(projectedFeature):
            arcpy.Project_management(feature, projectedFeature, "GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]", "", "", "PRESERVE_SHAPE", "", "NO_VERTICAL")
             
        return projectedFeature
        
        
def get_points_manifest_fields():

    fieldnames = []
    cFields = arcpy.ListFields(PointsManifest)
    for field in cFields:
        fieldnames.append(field.name)

    return fieldnames





def remove_duplicate_parcels(MergedParcels):

    uniqueList=[]
    duplicates=[]
    with arcpy.da.UpdateCursor(MergedParcels,["PARCEL_ID","APN","TYPE_CODE"]) as cursor:
        for row in cursor:
            if row[1] not in uniqueList:
                uniqueList.append(row[1])
            else:
                duplicates.append(row[1])
                cursor.deleteRow()


    arcpy.AddWarning("{} duplicate parcels were removed from merged parcel dataset.".format(len(duplicates)))

    return None

def remove_vacant_parcels(Parcels):


    arcpy.MakeFeatureLayer_management(Parcels, "points_lyr")
    arcpy.SelectLayerByAttribute_management("points_lyr", "NEW_SELECTION", "PROP_IND = '80' OR PROP_IND = '70'")
    arcpy.DeleteRows_management("points_lyr")
    arcpy.SelectLayerByAttribute_management("points_lyr", "NEW_SELECTION", "PROP_IND_T IS NULL")
    arcpy.DeleteRows_management("points_lyr")


    arcpy.AddMessage("Deleted parcels with the following Property Indicators: Vacant, Agricultural, NULL.")

    return None


def remove_nonresidential_parcels(Parcels):
    arcpy.MakeFeatureLayer_management(Parcels, "points_lyr")
    arcpy.SelectLayerByAttribute_management("points_lyr", "NEW_SELECTION", "PROP_IND = '0' OR PROP_IND = '00' OR PROP_IND = '50' OR PROP_IND = '51' OR PROP_IND = '52' OR PROP_IND = '53' OR PROP_IND = '54' OR PROP_IND = '90' OR PROP_IND = '20' OR PROP_IND = '23' OR PROP_IND = '24' OR PROP_IND = '25' OR PROP_IND = '26' OR PROP_IND = '27' OR PROP_IND = '28' OR PROP_IND = '29' OR PROP_IND = '30' OR PROP_IND = '31' OR PROP_IND = '32'")
    arcpy.AddMessage("Deleted non-residential parcels.")
    arcpy.DeleteRows_management("points_lyr")
    return None


def delete_temp_files():
    if arcpy.Exists(GDB + "\\tempfeature_WGS1984"):
        arcpy.Delete_management(GDB + "\\tempfeature_WGS1984")

    delList = arcpy.ListFeatureClasses("ParcelPoints_*")
    if len(delList) > 0:
        for item in delList:
            arcpy.Delete_management(item)

    return None


def main_loop():
    start_time = time.time()
    DateToday = get_date()


    arcpy.MakeFeatureLayer_management(mi,"mi_lyr")
    arcpy.MakeFeatureLayer_management(pgv,"pgv_lyr")
    arcpy.MakeFeatureLayer_management(pga,"pga_lyr")




    #IA Parcels
    if str(Boo1) == 'true':
        
        
        (IntersectingCounties, Count) = county_intersection("mi_lyr")
        arcpy.AddMessage("{} impacted counties.".format(Count))


        CountiesList=[]
        with arcpy.da.SearchCursor(IntersectingCounties,["STATEFP","COUNTYFP"]) as cursor:
            for row in cursor:
                print("{:2}{:3}".format(row[0],row[1]))
                CountiesList.append("{:2}{:3}".format(row[0],row[1]))

                
        fieldnames = get_points_manifest_fields()

        arcpy.AddMessage("Intersecting ShakeMap layer with parcel dataset.")
        
        ParcelDatasetList = Environ.get_parcels_for_download(CountiesList)

        with arcpy.da.SearchCursor(IntersectingCounties,["STATEFP","COUNTYFP"]) as cursor:
            for row in cursor:
                print("{:2}{:3}".format(row[0],row[1]))
                CountiesList.append("{:2}{:3}".format(row[0],row[1]))


        if Environment == "AWS":
            temp_files = Environ.retrieve_geopackages(ParcelDatasetList, AWS.bucket)
            ParcelDatasetList = temp_files
            
        Environ.copy_parcels_by_intersection(ParcelDatasetList, "mi_lyr", Count)

        
        MergedParcels = Environ.merge_parcels()
        arcpy.AddMessage("Parcel data from impacted counties merged into one dataset: {}".format(MergedParcels))

        
        delete_temp_files()
        

        if Environment == "Static":
            remove_vacant_parcels(MergedParcels)
            #remove_nonresidential_parcels(MergedParcels)
            remove_duplicate_parcels(MergedParcels)

    


    #Mobile Homes
    
    if str(Boo2) == 'true':

        arcpy.AddMessage("-------------------------------------")
        arcpy.AddMessage("Intersecting ShakeMap layer with Mobile Home Parks dataset.")
        arcpy.MakeFeatureLayer_management(MobileHomeParks,"MobileHomeParks_lyr")


        IntersectingMobileHomeParks = arcpy.SelectLayerByLocation_management("MobileHomeParks_lyr","INTERSECT","mi_lyr","","NEW_SELECTION")
        Count = int(arcpy.GetCount_management(IntersectingMobileHomeParks)[0])

        if Count > 0:
            arcpy.CopyFeatures_management(IntersectingMobileHomeParks,"IA_MobileHomeParks")
            arcpy.AddMessage("{} Mobile Home Parks intersect with ShakeMap layer. Copying data to user-defined workspace.".format(Count))

            
            #arcpy.AddField_management("IA_MobileHomeParks", "STATE_FULL","TEXT","","",50,"State")
            #arcpy.AddField_management("IA_MobileHomeParks","RES_NONRES","TEXT","","","","Occupancy Type")
            #with arcpy.da.UpdateCursor("IA_MobileHomeParks",["STATE","COUNTY","STATE_FULL","RES_NONRES"]) as cursor:
            #    for row in cursor:
            #        StateAbbrev = row[0]
            #        if StateAbbrev in StateList:
            #            print(StateAbbrev)
                   
            #            row[2] = "{}".format(StateList[StateAbbrev])
            #            row[1] = "{}".format(row[1].capitalize())
            #            row[3] = "MOBILE HOME PARK"
            #            cursor.updateRow(row)

            #arcpy.AddField_management("IA_MobileHomeParks","RES_NONRES","TEXT","","","","Occupancy Type")


        else:
            arcpy.AddMessage("0 Mobile Home Parks intersect with ShakeMap layer.")



    #################################### PARCELS - ADD MI, PGA, PGV INFO ##########################
        
    if str(Boo1) == 'true':

        arcpy.MakeFeatureLayer_management(GDB+"\\IA_Parcels", "Parcels_Layer")
        arcpy.SpatialJoin_analysis("Parcels_Layer", "mi_lyr", GDB+"\\IA_Parcels_MI", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_Parcels_MI", "PARAMVALUE", "MI", "MI", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_Parcels_MI", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_Parcels")

        arcpy.MakeFeatureLayer_management(GDB+"\\IA_Parcels_MI", "Parcels_Layer")
        arcpy.SpatialJoin_analysis("Parcels_Layer", "pga_lyr", GDB+"\\IA_Parcels_PGA", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_Parcels_PGA", "PARAMVALUE", "PGA", "PGA", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_Parcels_PGA", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_Parcels_MI")

        arcpy.MakeFeatureLayer_management(GDB+"\\IA_Parcels_PGA", "Parcels_Layer")
        arcpy.SpatialJoin_analysis("Parcels_Layer", "pgv_lyr", GDB+"\\IA_Parcels", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_Parcels", "PARAMVALUE", "PGV", "PGV", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_Parcels", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_Parcels_PGA")
        
        

        # Get MI as Integer Field
        arcpy.AddField_management(GDB+"\\IA_Parcels", "MI_INT", "SHORT", "", "", "", "MI_int")
        arcpy.CalculateField_management(GDB+"\\IA_Parcels", "MI_INT", "math.floor( !MI! )", "PYTHON_9.3", "")






    #################################### MOBILE HOME PARKS - ADD MI, PGA, PGV INFO ##########################
        
    if str(Boo2) == 'true':

        arcpy.MakeFeatureLayer_management(GDB + "\\IA_MobileHomeParks", "MobileHomeParks_Layer")
        arcpy.SpatialJoin_analysis("MobileHomeParks_Layer", "mi_lyr", GDB + "\\IA_MobileHomeParks_MI", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_MobileHomeParks_MI", "PARAMVALUE", "MI", "MI", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_MobileHomeParks_MI", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_MobileHomeParks")

        arcpy.MakeFeatureLayer_management(GDB+"\\IA_MobileHomeParks_MI", "MobileHomeParks_Layer")
        arcpy.SpatialJoin_analysis("MobileHomeParks_Layer", "pga_lyr", GDB+"\\IA_MobileHomeParks_PGA", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_MobileHomeParks_PGA", "PARAMVALUE", "PGA", "PGA", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_MobileHomeParks_PGA", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_MobileHomeParks_MI")

        arcpy.MakeFeatureLayer_management(GDB+"\\IA_MobileHomeParks_PGA", "MobileHomeParks_Layer")
        arcpy.SpatialJoin_analysis("MobileHomeParks_Layer", "pgv_lyr", GDB+"\\IA_MobileHomeParks", "JOIN_ONE_TO_ONE", "KEEP_ALL","")
        arcpy.AlterField_management(GDB+"\\IA_MobileHomeParks", "PARAMVALUE", "PGV", "PGV", "DOUBLE", "8", "NULLABLE", "false")
        arcpy.DeleteField_management(GDB+"\\IA_MobileHomeParks", "AREA;PERIMETER;PGAPOL_;PGAPOL_ID;GRID_CODE")
        arcpy.Delete_management(GDB+"\\IA_MobileHomeParks_PGA")
    

        # Get MI as Integer Field
        arcpy.AddField_management(GDB+"\\IA_MobileHomeParks", "MI_INT", "SHORT", "", "", "", "MI_int")
        arcpy.CalculateField_management(GDB+"\\IA_MobileHomeParks", "MI_INT", "math.floor( !MI! )", "PYTHON_9.3", "")







if __name__ == "__main__":
    # if we are running as a commandline tool this routine will run
    
    # pass any parameters in
    # main_loop(sys.argv)
    main_loop()










    

