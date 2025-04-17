import os
import geopandas as gpd    #used for handling geospatial Census Tract data
import geopandas as gpd    #used for handling geospatial Census Tract data
import pandas as pd
from scipy.stats import norm    #used to compute earthquake damage probability
import numpy as np
import time


# Step 1: Read in Data

## 1.a Read Damage functions Data
'''


# Step 1: Read in Data

## 1.a Read Damage functions Data

# The damage function variable table explained:

Each row represents a combination of building type and building code
building type refers to the (such as structure or materials of the building: frames, wall types)
building codes are the classification of its seismic codes
for example: HC (high code) is the most resistant. 
Each row represents a combination of building type and building code
building type refers to the (such as structure or materials of the building: frames, wall types)
building codes are the classification of its seismic codes
for example: HC (high code) is the most resistant. 

Each column (median moderate, median extensive, median complete ...) refers to a damage state
The values represents the PGA (Peak Ground Acceleration) value at which such damage state will occur.
For example, if MedianModerate = 0.22, it means given the building type and building code,
moderate damage can be expected at a PGA of 0.22.
Each column (median moderate, median extensive, median complete ...) refers to a damage state
The values represents the PGA (Peak Ground Acceleration) value at which such damage state will occur.
For example, if MedianModerate = 0.22, it means given the building type and building code,
moderate damage can be expected at a PGA of 0.22.

Those columns were followed by the beta columns (BetaSlight, BetaModerate, BetaExtensive...)
Those are lognormal standard deviations (used to compute confidence intervals or model uncertainty).
Small beta means this certain type of building has similar falling threshold (smaller uncertainty)
'''

def read_damage_functions(parent_dir):
    #dmgfvars = r"..\Tables\DamageFunctionVariables.csv"
    # parent_dir = os.path.dirname(os.getcwd())
    dmgfvars = os.path.join(parent_dir, "Tables", "DamageFunctionVariables.csv")
    dmgfvarsDF = pd.read_csv(dmgfvars)
    dmgfvarsDF = dmgfvarsDF.drop('Unnamed: 0', axis=1)
    list_bldgtypes = dmgfvarsDF["BLDG_TYPE"].unique()
    
    # Extract median cols, beta cols, and damage levels
    # List of cols with emdian estimates
    median_columns = [col for col in dmgfvarsDF.columns if col.lower().startswith('median')]

    # list of beta columns
    beta_columns = [col for col in dmgfvarsDF.columns if col.lower().startswith('beta')]

    # Return dataframe, list of building types, names of columns with median estimates and names of columns w/ beta estimates
    return dmgfvarsDF, list_bldgtypes,  median_columns, beta_columns


## 1.b Read Event Data
def read_event_data(parent_dir, eventid = 'nc72282711'):
    """
    Read event data from a GPKG file.
    """
    #TODO: o3 results might be switched to a .csv file so might need to update this accordingly!

    
    event_dir = os.path.join(parent_dir, 'ShakeMaps', eventid)

    # Update with the actual path
    GPKG_PATH = os.path.join(event_dir, "o3_building_clip_analysis.csv")

    # Read the layer you want to inspect
    # tract_shakemap_mmi, tract_shakemap_pga, tract_shakemap_pgv --> same idea
    gdf = pd.read_csv(GPKG_PATH)

    return gdf


def main(parent_dir, eventid):

    '''
    This function:
    1. Reads in data ()'''

    # Set UP:
    # list of the levels - used for renaming variables 
    pga_levels = ['slight', 'mod', 'ext', 'comp']


    # Read in Data
    dmgfvarsDF, list_bldgtypes,  median_columns, beta_columns = read_damage_functions(parent_dir)
    event_results = read_event_data(parent_dir, eventid)

    '''
    Assumption 1:

    Each building type (W1, W2 etc..) has multiple relevant rows for different seismic codes
    When available, we're keeping the highest code (HC). If that's not available, we're keeping MC etc..
    '''

   # Define priority order for BUILDINGCO
    priority_order = {"HC": 1, "MC": 2, "LC": 3, "PC": 4}

    # Sort by BLDG_TYPE and priority of BUILDINGCO
    dmgfvarsDF["priority"] = dmgfvarsDF["BUILDINGCO"].map(priority_order)
    dmgfvarsDF = dmgfvarsDF.sort_values(["BLDG_TYPE", "priority"])

    # Keep only the first occurrence of each BLDG_TYPE (i.e., highest priority)
    dmgfvars_hc = dmgfvarsDF.groupby("BLDG_TYPE").first().reset_index().drop(columns=["priority"])

    
    # Adding missing columns from o3 results
    #TODO: need to fix these in o3 instead of here
    
    # In the absence of a TOTAL column i will assume that adding all the categories leads to a total

    #event_results['Total_Num_Building'] = event_results['OTHER_OTHER'] + event_results['RESIDENTIAL_MULTI FAMILY'] + event_results['RESIDENTIAL_OTHER']+ event_results['RESIDENTIAL_SINGLE FAMILY']
    event_results['Total_Num_Building'] = event_results['TOTAL_BUILDING_COUNT']
    # ALSO IN THE ABSENCE OF PROPER COLUMNS FROM O3 --> I will multiply these here
    # Multiply total buildings by percentage columns to estimate counts
    #TODO: These need to happen in o3 and CANNOT be harcoded
    # building_types_o3 = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3', 'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L', 'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M', 'PC2H', 'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH']  # Get all the structure type columns

    # event_results[building_types_o3] = event_results[building_types_o3].multiply(event_results['Total_Num_Building'], axis=0)
    event_results.to_excel('event_results.xlsx', index=False)  # Save the modified DataFrame to an Excel file
    
    '''
    Step 1: Calculate the probability of each type of damage per building structure
    Goal: In this section, we would like to know what is the probability of each type of damage (slight, mod, compl, extensive) 
    given the type of structure and the min PGA for that tract
    '''

    # Initialize a dictionary to store computed probabilities
    prob_dict = {}

    # Loop through each building type

    #TODO: For future, add a check that all buildings in list_bldgtypes exist in o3 results. Otherwise errors might occur
    for bldg_type in list_bldgtypes:

        # Loop through each PGA level
        for i in range(len(pga_levels)):

            # Extract Beta for the current building type
            beta = dmgfvars_hc.loc[dmgfvars_hc['BLDG_TYPE'] == bldg_type, beta_columns[i]].item() #TODO: this assumes that the list of betas is ranked by damage level. Update this to use ilike to ensure prooper betas are being passed
            # Extract the correct median PGA threshold
            PGA_median = dmgfvars_hc.loc[dmgfvars_hc['BLDG_TYPE'] == bldg_type, median_columns[i]].item() #TODO: this assumes that the list of MEDIANS is ranked by damage level. Update this to use ilike to ensure prooper betas are being passed

            # Compute probability for the current building type and damage level
            prob_dict[f'P_{pga_levels[i].lower()}_{bldg_type}'] = norm.cdf((1 / beta) * np.log(event_results['min_intensity'] / PGA_median))

    # Add all computed probabilities to once
    df = pd.concat([event_results, pd.DataFrame(prob_dict)], axis=1)

    '''
    STEP 2: Estimate cumulative  number of buildings with certain levels of damage
    STEP 3: Get number of building for each category (subtract off the amount counted under other categories).
    '''
    # Initialize dictionaries to store computed values
    num_slight, num_moderate, num_extensive, num_complete = {}, {}, {}, {} # cumulative counts
    ex_slight, ex_moderate, ex_extensive, ex_complete = {}, {}, {}, {} # Exclusive counts (non-cumulative)

    # Loop through each building type to compute damage estimates
    for bldg_type in list_bldgtypes:
        # Cumulative damage estimates
        num_slight[f'numSlight_{bldg_type}'] = df[bldg_type] * df[f'P_slight_{bldg_type}']
        num_moderate[f'numModerate_{bldg_type}'] = num_slight[f'numSlight_{bldg_type}'] * df[f'P_mod_{bldg_type}']
        num_extensive[f'numExtensive_{bldg_type}'] = num_moderate[f'numModerate_{bldg_type}'] * df[f'P_ext_{bldg_type}']
        num_complete[f'numComplete_{bldg_type}'] = num_extensive[f'numExtensive_{bldg_type}'] * df[f'P_comp_{bldg_type}']

        # Exclusive damage estimates
        ex_slight[f'numSlight_{bldg_type}'] = num_slight[f'numSlight_{bldg_type}'] - num_moderate[f'numModerate_{bldg_type}']
        ex_moderate[f'numModerate_{bldg_type}'] = num_moderate[f'numModerate_{bldg_type}'] - num_extensive[f'numExtensive_{bldg_type}']
        ex_extensive[f'numExtensive_{bldg_type}'] = num_extensive[f'numExtensive_{bldg_type}'] - num_complete[f'numComplete_{bldg_type}']
        ex_complete[f'numComplete_{bldg_type}'] = num_complete[f'numComplete_{bldg_type}']

    # Assign all computed columns to df at once
    df = pd.concat([df, pd.DataFrame({**ex_slight, **ex_moderate, **ex_extensive, **ex_complete})], axis=1)

    '''
    STEP 4: Get the total number of buildings in each damage category 
    '''

    df["Total_Num_Building_Slight"] = df.filter(like="numSlight").sum(axis=1)
    df["Total_Num_Building_Moderate"] = df.filter(like="numModerate").sum(axis=1)
    df["Total_Num_Building_Extensive"] = df.filter(like="numExtensive").sum(axis=1)
    df["Total_Num_Building_Complete"] = df.filter(like="numComplete").sum(axis=1)

    df_final = df[['GEOID', 'max_intensity', 'min_intensity','mean_intensity', 'geometry',
               'Total_Num_Building', 'Total_Num_Building_Slight', 'Total_Num_Building_Moderate', 
               'Total_Num_Building_Extensive', 'Total_Num_Building_Complete']]
    
    #TODO: save this in folder directly potentially - wait to hear back from team on desired final output of o4
    return df_final



if __name__ == "__main__":
    start_time = time.time()
    parent_dir = os.path.dirname(os.getcwd())
    eventid = 'nc72282711'  # Example event ID, replace with actual event ID if needed
    print(main(parent_dir, eventid))
    print('Damage Assessment Successfully Conducted')
    print("--- {} seconds ---".format(time.time() - start_time))
