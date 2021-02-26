import arcpy


def main(parcels, DamFunctVars_dbf):

    # Combine Building Label and Building Code to create a lookup field for joining Damage Function Variables
    arcpy.AddField_management(parcels, "Lookup", "TEXT")
    arcpy.CalculateField_management(parcels, "Lookup","!BldgLabel! + !BldgCode!", "PYTHON")

    arcpy.JoinField_management(in_data=parcels, in_field="Lookup",
                               join_table=DamFunctVars_dbf,
                               join_field="Lookup_",
                               fields="MedianSlig;MedianMode;MedianExte;MedianComp;BetaSlight;BetaModera;BetaExtens;BetaComple")


if __name__ == "__main__":
    try: parcels
    except: parcels = r"C:\Users\madel\Documents\Earthquake Damage Assessment Model\transfer\transfer\NAPA_Parcels.shp"

    try: DamFunctVars_dbf
    except: DamFunctVars_dbf = r"C:\Users\madel\PycharmProjects\Earthquake_Model\Tables\DamageFunctionVariables.dbf"

    main(parcels, DamFunctVars_dbf)
