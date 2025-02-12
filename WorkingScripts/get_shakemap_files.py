
def get_shakemap_files(ShakeMapDir):
    """
    Generate file paths for ShakeMap shapefiles in the given directory.

    Args:
        ShakeMapDir (str): Path to the ShakeMap directory. The ShakeMapDir variable gets defined and stored in get_file_paths.py

    Returns:
        tuple: Paths to 'mi.shp', 'pgv.shp', and 'pga.shp' files.
    """
    
    mi = "{}\mi.shp".format(ShakeMapDir)
    pgv = "{}\pgv.shp".format(ShakeMapDir)
    pga = "{}\pga.shp".format(ShakeMapDir)
    return mi, pgv, pga
