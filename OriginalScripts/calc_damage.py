import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as ss
import math
import arcpy


def main(parcels):

    arcpy.AddField_management(parcels, "P_Slight", "DOUBLE")
    arcpy.AddField_management(parcels, "P_Moderate", "DOUBLE")
    arcpy.AddField_management(parcels, "P_Extensiv", "DOUBLE")
    arcpy.AddField_management(parcels, "P_Complete", "DOUBLE")
    arcpy.AddField_management(parcels, "DmgCat", "TEXT")

    with arcpy.da.UpdateCursor(parcels, ['MedianSlig','MedianMode','MedianExte','MedianComp',\
                                         'BetaSlight','BetaModera','BetaExtens','BetaComple','PGA',\
                                         'P_Slight','P_Moderate','P_Extensiv','P_Complete']) as cursor:
        for row in cursor:

            PGA = row[8]

            Bslight = row[4]
            MedianSlight = row[0]
            Bmoderate = row[5]
            MedianModerate = row[1]
            Bextensive = row[6]
            MedianExtensive = row[2]
            Bcomplete = row[7]
            MedianComplete = row[3]

            SlightX = (1 / Bslight) * math.log(PGA / MedianSlight)
            ModerateX = (1 / Bmoderate) * math.log(PGA / MedianModerate)
            ExtensiveX = (1 / Bextensive) * math.log(PGA / MedianExtensive)
            CompleteX = (1 / Bcomplete) * math.log(PGA / MedianComplete)

            Slight = ss.norm.cdf(SlightX)  # the normal cdf
            Moderate = ss.norm.cdf(ModerateX)  # the normal cdf
            Extensive = ss.norm.cdf(ExtensiveX)  # the normal cdf
            Complete = ss.norm.cdf(CompleteX)  # the normal cdf

            row[9] = Slight
            row[10] = Moderate
            row[11] = Extensive
            row[12] = Complete

            cursor.updateRow(row)

        row = None
        cursor = None

    with arcpy.da.UpdateCursor(parcels, ['P_Slight', 'P_Moderate', 'P_Extensiv', 'P_Complete', 'DmgCat']) as cursor:

        for row in cursor:
            P_Slight = row[0]
            P_Moderate = row[1]
            P_Extensive = row[2]
            P_Complete = row[3]

            if P_Slight < 0.5:
                Category = 'Unaffected'
            if P_Slight >= 0.5:
                Category = 'Affected'
            if P_Moderate >= 0.5:
                Category = 'Minor'
            if P_Extensive >= 0.5:
                Category = 'Major'
            if P_Complete >= 0.5:
                Category = 'Destroyed'

            row[4] = Category

            cursor.updateRow(row)

        row = None
        cursor = None

    return



if __name__ == "__main__":
    try: parcels
    except: parcels = r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\transfer\transfer\NAPA_Parcels.shp"

    main(parcels)
