import arcpy


def join_seis_code(JoinFrom_features, JoinTo_features, ToField):

    arcpy.AddField_management(in_table=JoinTo_features,
                              field_name=ToField,
                              field_type="TEXT",
                              field_precision="",
                              field_scale="", field_length="",
                              field_alias="",
                              field_is_nullable="NULLABLE",
                              field_is_required="NON_REQUIRED",
                              field_domain="")

    SeisCodeList = ["A", "B", "C", "D0", "D1", "D2", "E"]

    arcpy.MakeFeatureLayer_management(in_features=JoinFrom_features, out_layer="JoinFrom_Lyr32")
    arcpy.MakeFeatureLayer_management(in_features=JoinTo_features, out_layer="JoinTo_Lyr32")

    for code in SeisCodeList:
        clause = """ "SDC" = '{}' """.format(code)
        arcpy.SelectLayerByAttribute_management(in_layer_or_view="JoinFrom_Lyr",
                                                selection_type="NEW_SELECTION",
                                                where_clause=clause)

        arcpy.SelectLayerByLocation_management(in_layer="JoinTo_Lyr",
                                               overlap_type="INTERSECT",
                                               select_features="JoinFrom_Lyr",
                                               search_distance="",
                                               selection_type="NEW_SELECTION",
                                               invert_spatial_relationship="NOT_INVERT")

        with arcpy.da.UpdateCursor(in_table="JoinTo_Lyr", field_names=["{}".format(ToField)]) as cursor:
            for row in cursor:
                row[0] = code
                cursor.updateRow(row)
