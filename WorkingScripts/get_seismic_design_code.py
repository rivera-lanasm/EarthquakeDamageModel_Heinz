import arcpy

SeisCodes = r"C:\Data\2006_2009_IRC-Design_Categories.shape\IRC2006_2009_dissolved.shp"

# List of structure types that contain all building codes (HC, MC, LC, PC)
List_Class1 = ["C1H", "C1M", "C1L",
               "C2H", "C2M", "C2L",
               "MH", "PC1",
               "PC2H", "PC2M", "PC2L",
               "RM1M", "RM1L",
               "RM2H", "RM2M", "RM2L",
               "S1H", "S1M", "S1L",
               "S2H", "S2M", "S2L",
               "S3",
               "S4H", "S4M", "S4L",
               "W1", "W2"]
List_Class1 = [unicode(s) for s in List_Class1]

# List of structure types that only contain building codes (LC, PC)
List_Class2 = ["C3H", "C3M", "C3L",
               "S5H", "S5M", "S5L",
               "URMM", "URML"]
List_Class2 = [unicode(s) for s in List_Class2]


class Post1975:

    def __init__(self):
        pass

    Dict_Class1 = {"A": "PC",
                   "B": "LC",
                   "C": "LC",
                   "D0": "MC",
                   "D1": "MC",
                   "D2": "HC",
                   "E": "HC"}

    Dict_Class2 = {"A": "PC",
                   "B": "PC",
                   "C": "PC",
                   "D0": "LC",
                   "D1": "LC",
                   "D2": "LC",
                   "E": "LC"}


class Pre1975:

    def __init__(self):
        pass

    Dict_Class1 = {"A": "PC",
                   "B": "PC",
                   "C": "LC",
                   "D0": "LC",
                   "D1": "MC",
                   "D2": "MC",
                   "E": "MC"}

    Dict_Class2 = {"A": "PC",
                   "B": "PC",
                   "C": "PC",
                   "D0": "LC",
                   "D1": "LC",
                   "D2": "LC",
                   "E": "LC"}


class Pre1941:

    def __init__(self):
        pass

    Dict_Class1 = {"A": "PC",
                   "B": "PC",
                   "C": "PC",
                   "D0": "PC",
                   "D1": "PC",
                   "D2": "PC",
                   "E": "PC"}

    Dict_Class2 = {"A": "PC",
                   "B": "PC",
                   "C": "PC",
                   "D0": "PC",
                   "D1": "PC",
                   "D2": "PC",
                   "E": "PC"}


def main(buildings_lyr):

    # List of Seismic Design Codes: A, B, C, D0, D1, D2, E
    CodeList = ['A', 'B', 'C', 'D0', 'D1', 'D2', 'E']

    # Make Layers for Spatial Intersections
    arcpy.MakeFeatureLayer_management(SeisCodes, "SeisCodes")

    for code in CodeList:
        clause = """ SDC = '{}' """.format(code)
        SelectedSeisCode = arcpy.SelectLayerByAttribute_management("SeisCodes","NEW_SELECTION", clause)

        SelectedBldgs = arcpy.SelectLayerByLocation_management(buildings_lyr, "WITHIN", SelectedSeisCode, \
                                                               "", "NEW_SELECTION", "")

        with arcpy.da.UpdateCursor(SelectedBldgs, ["SeisCode"]) as cursor:
            for row in cursor:
                row[0] = code
                cursor.updateRow(row)

            row = None
            cursor = None

        arcpy.SelectLayerByAttribute_management("SeisCodes", "CLEAR_SELECTION")
        arcpy.SelectLayerByAttribute_management(buildings_lyr, "CLEAR_SELECTION")

    # Select NULL seismic codes and calculate default seismic code to be D0
    NullSeisCodes = arcpy.SelectLayerByAttribute_management(buildings_lyr, "NEW_SELECTION", "SeisCode IS NULL")
    arcpy.CalculateField_management(NullSeisCodes, "SeisCode", "'D0'","PYTHON", "")
    arcpy.SelectLayerByAttribute_management(buildings_lyr, "CLEAR_SELECTION")

    with arcpy.da.UpdateCursor(buildings_lyr, ["YR_BLT", "BldgLabel", "SeisCode", "BldgCode"]) as cursor:
        for row in cursor:

            year_built = row[0]
            buildingType = row[1]
            # assign class for seismic code lookup table based on year built
            if year_built:
                if year_built <= 1941:
                    Yr = Pre1941()
                elif year_built <= 1975:
                    Yr = Pre1975()
                else:
                    Yr = Post1975()
            elif not year_built:
                Yr = Post1975()

            if not buildingType == None:
                SDC = row[2]

                if buildingType in List_Class1:
                    BC = Yr.Dict_Class1[SDC]
                    row[3] = BC
                    cursor.updateRow(row)
                elif buildingType in List_Class2:
                    BC = Yr.Dict_Class2[SDC]
                    row[3] = BC
                    cursor.updateRow(row)

            else:
                pass

        row = None
        cursor = None

                
    # arcpy.AddField_management(buildings,"Pslight","DOUBLE")
    # arcpy.AddField_management(buildings,"Pmoderate","DOUBLE")
    # arcpy.AddField_management(buildings,"Pextensive","DOUBLE")
    # arcpy.AddField_management(buildings,"Pcomplete","DOUBLE")


if __name__ == "__main__":
    try: buildings_lyr
    except:
        buildings_lyr = "buildings_lyr"
        arcpy.MakeFeatureLayer_management(r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\ParcelBldgType\working.gdb\ParcelPoints_CA_Placer_1", buildings_lyr)

    main(buildings_lyr)
    #logger.debug("All Done")