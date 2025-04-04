import arcpy
import os 
import shutil

# python env
# C:\Users\river\AppData\Local\ESRI\conda\envs\arcgispro-py3-heinz\python.exe

if __name__ == "__main__":

    # Define paths
    lpk_path = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\USA_Counties.lpk"
    output_folder = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\county_shp"
    output_shapefile = f"{output_folder}\\USA_Counties.shp"

    # Unpack the Layer Package
    # unpacked_folder = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\tmp\county_shp\"
    arcpy.management.ExtractPackage(lpk_path, output_folder)

    # Locate the .gdb directory after extraction
    gdb_path = None
    for item in os.listdir(output_folder):
        if item.endswith(".gdb"):
            gdb_path = os.path.join(output_folder, item)
            break

    # Set workspace to the .gdb directory
    arcpy.env.workspace = gdb_path

    # List all feature classes within the .gdb
    feature_classes = arcpy.ListFeatureClasses()
    feature_to_convert = feature_classes[0]

    arcpy.conversion.FeatureClassToShapefile([feature_to_convert], output_folder)

    print("Conversion completed successfully!")

    # copy to destination
    source = "path/to/source/file.shp"  # Original file path
    # Target file path
    destination = "C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\Data\esri_2019_detailed_counties\2019detailedcounties.shp" 

    shutil.copy(source, destination)
    print("File copied successfully!")

