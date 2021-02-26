import arcpy
from get_building_label import main as get_building_label_main
from get_damage_function_vars import main as get_damage_function_vars_main
from calc_damage import main as calc_damage_main


parcels_withPGA = arcpy.GetParameterAsText(0)
DamFunctVars_dbf = r"" #location of damage function variables

arcpy.AddMessage('Beginning Earthquake Damage Assessment Model.')
arcpy.AddMessage('Getting Building Attributes for Parcels.')
get_building_label_main(parcels_withPGA)
arcpy.AddMessage('Getting Damage Function Variables for Parcels.')
get_damage_function_vars_main(parcels_withPGA, DamFunctVars_dbf)
arcpy.AddMessage('Calculating Damage Categories for Parcels.')
calc_damage_main(parcels_withPGA)
arcpy.AddMessage('Earthquake Damage Assessment Model Completed.')



