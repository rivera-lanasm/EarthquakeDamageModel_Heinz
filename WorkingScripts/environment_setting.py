#!/usr/bin/env python
# coding: utf-8

# In[19]:


import os
import subprocess
import sys


# In[20]:


parent_dir = os.path.dirname(os.getcwd())


# In[ ]:


# check if directory exist if not make it, return path
def make_directories(parent_dir):
    """Create directories for data storage if they do not exist."""
    data_path = os.path.join(parent_dir, 'Data')
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    
    building_data_csv = os.path.join(data_path, 'building_data_csv')
    building_data_gdb = os.path.join(data_path, 'building_data_gdb')
    building_stock_data = os.path.join(data_path, 'building_stock_data')
    census_shp = os.path.join(data_path, 'census_shp')
    extracted_census_shp = os.path.join(data_path, 'extracted_census_shp')
    merged_shapefile = os.path.join(data_path, 'merged_shapefile')
    if not os.path.exists(building_data_csv):
        os.makedirs(building_data_csv)
    if not os.path.exists(building_data_gdb):
        os.makedirs(building_data_gdb)
    if not os.path.exists(building_stock_data):
        os.makedirs(building_stock_data)
    if not os.path.exists(census_shp):
        os.makedirs(census_shp)
    if not os.path.exists(extracted_census_shp):
        os.makedirs(extracted_census_shp)
    if not os.path.exists(merged_shapefile):
        os.makedirs(merged_shapefile)
    
    ShakeMaps = os.path.join(parent_dir, 'ShakeMaps')
    if not os.path.exists(ShakeMaps):
        os.makedirs(ShakeMaps)

    return building_data_csv, building_data_gdb, building_stock_data


# In[ ]:


def install_req(parent_dir):
    """Install required packages for the script."""
    # read requirements.txt
    # and install the packages
    requirements_file = os.path.join(parent_dir, 'requirements.txt')
    required_packages = []
    with open(requirements_file, 'r') as f:
        for line in f:
            package = line.strip()
            if package and not package.startswith('#'):
                required_packages.append(package)
    for package in required_packages:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])


# In[ ]:


def setting_env(parent_dir):
    """Set up the environment for the script."""
    make_directories(parent_dir)
    install_req(parent_dir)
    print("Environment is set up successfully.")


# In[ ]:


if __name__ == "__main__":
    setting_env(parent_dir)

