import arcpy
from get_seismic_design_code import main as get_seis_code


def add_bldg_fields(feat, listTextFields):
    print('Adding fields.')

    for textField in listTextFields:
        arcpy.AddField_management(feat, textField, "TEXT")
    return


def make_dictionaries():
    # create empty dict to contain Construction Type and Exterior Wall lookup tables
    ConstrTyp_dict = {}
    ExtWall_dict = {}

    # Populate dicts with lookup table data - CONSTRUCTION TYPE
    ConstrType_dbf = r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\ParcelBldgType\CNSTR_lookup.dbf"
    with arcpy.da.SearchCursor(ConstrType_dbf, ["CNSTR_Code", "BldgCatego", "BldgSubCat", "BldgType"]) as cursor:
        for row in cursor:
            ConstrTyp_dict.update({row[0]: [row[1], int(row[2]), row[3]]})
            # dict will have keys = Construction Type Code and
            #  values = Bldg Cat, BldgSubCat, BldgType
        row = None
        cursor = None

    ExtWall_dbf = r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\ParcelBldgType\EXTNW_lookup.dbf"
    with arcpy.da.SearchCursor(ExtWall_dbf, ["EXTNW_Code", "BldgCatego", "BldgSubCat", "BldgType"]) as cursor:
        for row in cursor:
            ExtWall_dict.update({row[0]: [row[1], int(row[2]), row[3]]})
            # dict will have keys = Exterior Wall Type Code and
            #  values = Bldg Cat, BldgSubCat, BldgType
        row = None
        cursor = None

    return ConstrTyp_dict, ExtWall_dict


def lookup_construction_type(parcels, dictionary):
    print('Looking up Building Type from Construction Type.')
    with arcpy.da.UpdateCursor(parcels, ["CONSTR_TYP", "BldgCat", "BldgSubCat", "BldgType", "STOP"]) as cursor:
        for row in cursor:
            CONSTR_TYP = row[0]
            if (CONSTR_TYP == ' ') or (CONSTR_TYP == ''):
                continue
            if (CONSTR_TYP is not None) and (len(CONSTR_TYP) > 1):
                BldgCat = dictionary[CONSTR_TYP][0]
                BldgSubCat = dictionary[CONSTR_TYP][1]
                BldgType = dictionary[CONSTR_TYP][2]
                row[1] = BldgCat
                row[2] = BldgSubCat
                row[3] = BldgType
                row[4] = 'Y'
                cursor.updateRow(row)

        row = None
        cursor = None

    return


def lookup_exteriorwall_type(parcels, dictionary):
    print('Looking up Building Type from Exterior Wall Type.')

    with arcpy.da.UpdateCursor(parcels, ["CONSTR_TYP", "EXT_WALLS", "BldgCat", "BldgSubCat", "BldgType", "STOP"]) as cursor:
        for row in cursor:
            CONSTR_TYP = row[0]
            EXT_WALLS = row[1]

            # if construction type exists, use that instead of exterior wall type
            if (CONSTR_TYP is not None) and (len(CONSTR_TYP) > 1):
                continue
            elif (EXT_WALLS is not None) and (len(EXT_WALLS) > 1):
                BldgCat = dictionary[EXT_WALLS][0]
                BldgSubCat = dictionary[EXT_WALLS][1]
                BldgType = dictionary[EXT_WALLS][2]
                row[2] = BldgCat
                row[3] = BldgSubCat
                row[4] = BldgType
                row[5] = 'Y'
                cursor.updateRow(row)

        row = None
        cursor = None

    return


def get_height(parcels):
    print('Getting building height from number of stories.')

    with arcpy.da.UpdateCursor(parcels, ["STORY_NBR", "BldgHeight", "LAND_USE"]) as cursor:
        for row in cursor:
            stories = row[0]

            if (stories is not None) and (stories >= 1):

                if stories <= 3:
                    row[1] = "L"
                elif stories <= 7:
                    row[1] = "M"
                else:
                    row[1] = "H"

                cursor.updateRow(row)

            if (not stories) or (stories == 0):

                # LAND_USE 116 = Mid-Rise Condo
                if row[2] == '116':
                    row[1] = "M"

                # LAND_USE 117 = High-Rise Condo
                if row[2] == '117':
                    row[1] = "H"

                cursor.updateRow(row)

        row = None
        cursor = None

    return


def landuse_MH(parcels):
    print("Categorizing Mobile/Manufactured Homes based on land use.")

    with arcpy.da.UpdateCursor(parcels, ["LAND_USE", "BldgCat", "BldgSubCat", "BldgHeight", "STOP"]) as cursor:
        for row in cursor:
            landuse = row[0]

            if (landuse is not None) and (len(landuse) > 1):

                # LAND_USE 137 = Mobile Home
                # LAND_USE 138 = Manufactured Home
                if (landuse == '137' or landuse == '138') and (row[4] != 'Y'):
                    row[1] = "MH"   # building category
                    row[2] = " "   # building subcategory
                    row[3] = " "   # building height
                    row[4] = "Y"   # STOP = yes
                    cursor.updateRow(row)
        row = None
        cursor = None

    return


def landuse_W(parcels):
    print("Categorizing Wood buildings based on land use.")

    with arcpy.da.UpdateCursor(parcels, ["LAND_USE", "BldgCat", "BldgSubCat", "BldgHeight", "STOP"]) as cursor:
        for row in cursor:
            landuse = row[0]
            if (landuse is not None) and (len(landuse) > 1):

                # LAND_USE 109 = Cabin
                # LAND_USE 163 = Single Family Residence
                if (landuse == '109' or landuse == '163') and (row[4] != 'Y'):
                    row[1] = "W"   # building category
                    row[2] = "1"   # building subcategory
                    row[3] = " "   # building height
                    row[4] = "Y"   # STOP = yes
                    cursor.updateRow(row)
        row = None
        cursor = None

    return


def subCat_for_Ws(parcels_lyr):
    print("Finding large wooden buildings (W2).")
    clause = """ (BldgCat = 'W') AND (GR_SQ_FT IS NOT NULL) AND (GR_SQ_FT>= 5000) """
    arcpy.SelectLayerByAttribute_management(parcels_lyr, "NEW_SELECTION", clause)
    arcpy.CalculateField_management(parcels_lyr, "BldgSubCat", "2", "PYTHON")
    arcpy.SelectLayerByAttribute_management(parcels_lyr, "CLEAR_SELECTION")



def getBldgType_for_Ws(parcels_lyr):
    print("Generating Building Type from Building Category and Building SubCategory.")
    clause = """ ((BldgType IS NULL) OR (BldgType = '')) AND (STOP = 'Y') """
    arcpy.SelectLayerByAttribute_management(parcels_lyr, "NEW_SELECTION", clause)
    arcpy.CalculateField_management(parcels_lyr, "BldgType", "(!BldgCat!+ !BldgSubCat!).strip()", "PYTHON")
    arcpy.SelectLayerByAttribute_management(parcels_lyr, "CLEAR_SELECTION")


def add_default_height(parcels):
    print('Adding default height to remaining buildings.')
    with arcpy.da.UpdateCursor(parcels, ["BldgType", "BldgHeight"]) as cursor:
        for row in cursor:
            BldgType = row[0]

            if (BldgType is not None) and (len(BldgType) > 1):

                # default to "L" if null
                if not row[1]:
                    row[1] = 'L'
                if row[1] == ' ':
                    row[1] = 'L'
                if row[1] == ' ':
                    row[1] = 'L'

                # all building types that DO NOT have # stories (L, M, H)
                if BldgType == 'W1' or BldgType == 'W2' or BldgType == 'S3' or BldgType == 'MH' or BldgType == 'PC1':
                    row[1] = ' '

                # make sure that RM1 and URM building types do not have high rises
                if BldgType == 'RM1' or BldgType == 'URM':
                    if row[1] == 'H':
                        row[1] = 'M'

                cursor.updateRow(row)

        row = None
        cursor = None

    return


def remaining_building_categories(parcels_lyr):

    ## Classify LOW RISE or NULL HEIGHT buildings to W1
    UnclassifiedBldgs = arcpy.SelectLayerByAttribute_management(parcels_lyr, "NEW_SELECTION", "((BldgHeight IS NULL) OR (BldgHeight = '') OR (BldgHeight = 'L')) AND ((BldgCat IS NULL) OR (BldgCat = '') OR (BldgCat = ' '))")
    x = arcpy.GetCount_management(UnclassifiedBldgs)
    count_x = int(x[0])
    print('Number of remaining unclassified buildings (to become W1): {}'.format(count_x))

    with arcpy.da.UpdateCursor(UnclassifiedBldgs, \
                               ["BldgCat", "BldgSubCat", "BldgType","BldgHeight","BldgLabel","STOP"]) as cursor:

        # all buildings without a classification will default to W1
        for row in cursor:
            row[0] = 'W'
            row[1] = '1'
            row[2] = 'W1'
            row[3] = ' '
            row[4] = 'W1'
            row[5] = 'Y'

            cursor.updateRow(row)

        row = None
        cursor = None

    arcpy.SelectLayerByAttribute_management(parcels_lyr, "CLEAR_SELECTION")


    ## Classify MID RISE buildings (typically residential) to W2
    UnclassifiedBldgs = arcpy.SelectLayerByAttribute_management(parcels_lyr, "NEW_SELECTION",
                                                                "(BldgHeight = 'M') AND ((BldgCat IS NULL) OR (BldgCat = '') OR (BldgCat = ' '))")
    x = arcpy.GetCount_management(UnclassifiedBldgs)
    count_x = int(x[0])
    print('Number of remaining unclassified buildings (to become W2): {}'.format(count_x))

    with arcpy.da.UpdateCursor(UnclassifiedBldgs, \
                               ["BldgCat", "BldgSubCat", "BldgType", "BldgHeight", "BldgLabel", "STOP"]) as cursor:

        # all buildings without a classification will default to W1
        for row in cursor:
            row[0] = 'W'
            row[1] = '2'
            row[2] = 'W2'
            #row[3] = ''
            row[4] = 'W2'
            row[5] = 'Y'

            cursor.updateRow(row)

        row = None
        cursor = None

    arcpy.SelectLayerByAttribute_management(parcels_lyr, "CLEAR_SELECTION")


    ## Classify HIGH RISE buildings (typically condominiums) to S1H
    UnclassifiedBldgs = arcpy.SelectLayerByAttribute_management(parcels_lyr, "NEW_SELECTION",
                                                                "(BldgHeight = 'H') AND ((BldgCat IS NULL) OR (BldgCat = '') OR (BldgCat = ' '))")
    x = arcpy.GetCount_management(UnclassifiedBldgs)
    count_x = int(x[0])
    print('Number of remaining unclassified buildings (to become S1H): {}'.format(count_x))

    with arcpy.da.UpdateCursor(UnclassifiedBldgs, \
                               ["BldgCat", "BldgSubCat", "BldgType", "BldgHeight", "BldgLabel", "STOP"]) as cursor:

        # all buildings without a classification will default to W1
        for row in cursor:
            row[0] = 'S'
            row[1] = '1'
            row[2] = 'S1'
            # row[3] = ''
            row[4] = 'S1H'
            row[5] = 'Y'

            cursor.updateRow(row)

        row = None
        cursor = None

    arcpy.SelectLayerByAttribute_management(parcels_lyr, "CLEAR_SELECTION")

    return

def add_building_label(parcels):
    with arcpy.da.UpdateCursor(parcels, ["BldgType", "BldgHeight", "BldgLabel"]) as cursor:
        for row in cursor:
            BldgType = row[0]
            BldgHeight = row[1]
            BldgLabel = row[2]

            if (BldgType is None) or (BldgType == ''):
                continue

            if (BldgHeight is None) or (BldgHeight == ''):
                continue

            if (BldgLabel is not None) and (len(BldgLabel) > 1):
                continue

            BuildingLabel = BldgType + BldgHeight
            row[2] = BuildingLabel.strip()  # remove white space after

            cursor.updateRow(row)

        row = None
        cursor = None

    return


def main(parcels):

    # make dictionaries from lookup tables
    ConstrTyp_dict, ExtWall_dict = make_dictionaries()

    # # add all components for "Building Label" as fields
    # add_bldg_fields(parcels, ["SeisCode", "BldgCat", "BldgSubCat", "BldgType", "BldgHeight", "BldgCode", \
    #                           "BldgLabel", "STOP"])

    # ConstructionType Reader
    lookup_construction_type(parcels, ConstrTyp_dict)

    # ExteriorWallType Reader
    lookup_exteriorwall_type(parcels, ExtWall_dict)

    # get BldgHeight from Number of Stories
    get_height(parcels)

    # make layer of parcels
    arcpy.MakeFeatureLayer_management(parcels, "parcels_lyr")

    # assign mobile home Building Type to parcels based on land use code
    landuse_MH("parcels_lyr")

    # assign wooden Building Type to parcels based on land use code
    landuse_W("parcels_lyr")

    # all wooden Building Types are set to SubCat 1 for default. search for GrSqFt > 5000 to change SubCat to 2
    subCat_for_Ws("parcels_lyr")

    # if STOP = Y --> get the building type from the BldgCat & BldgSubCat
    getBldgType_for_Ws("parcels_lyr")

    # cleanup and add building height for rest of buildings
    add_default_height(parcels)

    # if no building category or height exists, default to W1
    remaining_building_categories("parcels_lyr")

    # combine building type with building height for building label
    add_building_label(parcels)

    # Add Seismic Code to Parcel (see script: get_seismic_design_code.py)
    get_seis_code("parcels_lyr")



if __name__ == "__main__":
    try: parcels
    except: parcels = r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\transfer\transfer\NAPA_Parcels.shp"

    main(parcels)