import os

def get_shakemap_dir():
    # Set file path to save ShakeMap zip files to

    # Check if a directory named "ShakeMaps" exists in the parent directory of the current working directory.
    # If the "ShakeMaps" directory exists, assign its path to the variable ShakeMapDir.
    if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')):
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    # If the "ShakeMaps" directory does not exist, create the directory and assign the path to the variable ShakeMapDir
    else:
        os.mkdir(os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps'))
        ShakeMapDir = os.path.join(os.path.dirname(os.getcwd()), 'ShakeMaps')

    return ShakeMapDir

if __name__ == "__main__":
    get_shakemap_dir()
