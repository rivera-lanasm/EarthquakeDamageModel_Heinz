import os
import geopandas as gp    #used for handling geospatial Census Tract data
import pandas as pd
from scipy.stats import norm    #used to compute earthquake damage probability
import numpy as np
import time
# import config

IdahoEventDir = r"C:\Users\river\CMU\rcross\EarthquakeDamageModel_Heinz\ShakeMaps_Testing\idaho2017shakemap_fortesting\shape"

# Import Spreadsheet with Hazus Building Type Breakdown per Tract
bldg_percentages_by_tract_csv = r"..\Tables\Building_Percentages_Per_Tract_ALLSTATES.csv"
bldg_percentages_by_tract_df = pd.read_csv(bldg_percentages_by_tract_csv)

'''
Ensures all Census Tract FIPS codes are properly formatted as 11-digit strings by adding leading zeros when needed
'''
#add leading zeroes to FIPS codes that do not have leading zeroes
bldg_percentages_by_tract_df["Tract_str"] = bldg_percentages_by_tract_df["Tract"].apply(str)
for fips in bldg_percentages_by_tract_df["Tract_str"].unique():
    if len(fips) == 11:    #fips code is already correct -> do nothing
        None
    elif len(fips) == 10:    #fips code miss a leading zero -> needed to be corrected
        # add leading zero to fips string
        newfips = "0" + fips
        idx = bldg_percentages_by_tract_df[bldg_percentages_by_tract_df["Tract_str"]==fips]["Tract_str"].index
        bldg_percentages_by_tract_df.loc[idx, "Tract_str"] = newfips

# Import Damage Function Variables Spreadsheet

# The damage function variable table explained:

# Each row represents a combination of building type and building code
# building type refers to the (such as structure or materials of the building: frames, wall types)
# building codes are the classification of its seismic codes
# for example: HC (high code) is the most resistant. 

# Each column (median moderate, median extensive, median complete ...) refers to a damage state
# The values represents the PGA (Peak Ground Acceleration) value at which such damage state will occur.
# For example, if MedianModerate = 0.22, it means given the building type and building code,
# moderate damage can be expected at a PGA of 0.22.

# Those columns were followed by the beta columns (BetaSlight, BetaModerate, BetaExtensive...)
# Those are lognormal standard deviations (used to compute confidence intervals or model uncertainty).
# Small beta means this certain type of building has similar falling threshold (smaller uncertainty)

dmgfvars = r"..\Tables\DamageFunctionVariables.csv"
dmgfvarsDF = pd.read_csv(dmgfvars)
dmgfvarsDF = dmgfvarsDF.drop('Unnamed: 0', axis=1)
list_bldgtypes = dmgfvarsDF["BLDG_TYPE"].unique()


def main(tracts_layer = "census_tract_max_mmi_pga_pgv_bldgcount", eventdir = IdahoEventDir):

    '''
    Performs earthquake damage assessment at the Census Tract level.

    This function:
    1. Loads Census Tract data containing earthquake shaking intensity and building counts from o3.
    2. Uses General Building Stock (GBS) percentages to estimate the number of buildings per type.
    3. Applies earthquake damage probability models to estimate damage levels for each structure.
    4. Aggregates results to classify tracts by damage severity.
    5. Saves the final damage assessment as a shapefile.

    Args:
        tracts_layer (str): Name of the geospatial layer with Census Tract data.
        eventdir (str): Path to the earthquake event directory.

    Returns:
        Saves the damage assessment results as a shapefile.
    '''
    
    gdb = os.path.join(eventdir, "eqmodel_outputs.gdb")

    # read geospacial census Tract datafrom gdb file
    # extract the list of unique census Tracts (FIPS codes)
    tracts = gp.read_file(gdb, layer = tracts_layer)
    tract_FIPS_list = tracts["FIPS"].unique()


    # initialize new Columns for Damage Assessment (building types + earthquake damage levels)
    newcols = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3',
               'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L',
               'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M', 'PC2H',
               'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH', 'Slight',
               'Moderate', 'Extensive', 'Complete']
    for col in newcols:
        tracts[col] = 0

    # process each tract individually
    # creates a new DataFrame containing only one census tract (the one currently being processed in the loop)
    for FIPS in tract_FIPS_list:
        subset = tracts[tracts["FIPS"] == FIPS]


        #extract necessary columns for current tract's damage assessment
        df = subset[["FIPS", "max_MMI", "max_PGA", "max_PGV", "min_PGA", "mean_PGA", "Point_Count", "geometry",
                     'W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3',
                     'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L',
                     'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M', 'PC2H',
                     'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH',
                     'Slight', 'Moderate', 'Extensive', 'Complete']]

        # find/match building type percentages for the current Census Tract
        subset_bldgpcts = bldg_percentages_by_tract_df[bldg_percentages_by_tract_df["Tract_str"] == FIPS]
        if len(subset_bldgpcts) == 0:        #if no matching building type percentages found for this tract -> skip this tract
            continue

        bldgtype_cols = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3',
                    'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L',
                    'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M', 'PC2H',
                    'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH']


        # compute number of buildings per type in current Tract
        # multiply total building count by percentage for each building type
        bldgcount = df["Point_Count"].item()                    # "Point_Count": the total number of buildings in this census Tract
        for col in bldgtype_cols:
            df[col] = bldgcount * subset_bldgpcts[col].iloc[0]


        maxPGA = df["max_PGA"].item()
        minPGA = df["min_PGA"].item()
        meanPGA = df["mean_PGA"].item()

        # This runs through each building type, assuming High Code but dropping to Medium, Low or Pre-Code depending
        # on what variables are available, then grabs the variables associated with that Building Type + Code

        # Then, plots the damage function curve and based on the Min or Max PGA, estimates the probability of damage
        # for that structure type. The probabilities are then multiplied by the number of structures in the tract.

        # Here is where the damage function variables data is used:
        # Used lognormal cumulative distribution function (CDF) to model damage.

        for BLDG_TYPE in list_bldgtypes:

            df_vars = dmgfvarsDF[(dmgfvarsDF["BLDG_TYPE"]==BLDG_TYPE) & (dmgfvarsDF["BUILDINGCO"]=="HC")]
            seiscode = "HC"
            if len(df_vars) == 0:
                df_vars = dmgfvarsDF[(dmgfvarsDF["BLDG_TYPE"]==BLDG_TYPE) & (dmgfvarsDF["BUILDINGCO"]=="MC")]
                seiscode = "MC"
                if len(df_vars) == 0:
                    df_vars = dmgfvarsDF[(dmgfvarsDF["BLDG_TYPE"]==BLDG_TYPE) & (dmgfvarsDF["BUILDINGCO"]=="LC")]
                    seiscode = "LC"
                    if len(df_vars) == 0:
                        df_vars = dmgfvarsDF[(dmgfvarsDF["BLDG_TYPE"]==BLDG_TYPE) & (dmgfvarsDF["BUILDINGCO"]=="PC")]
                        seiscode = "PC"

            #Beta
            Bslight = df_vars["BETASLIGHT"].item()
            Bmoderate = df_vars["BETAMODERA"].item()
            Bextensive = df_vars["BETAEXTENS"].item()
            Bcomplete = df_vars["BETACOMPLE"].item()
            #Median
            PGAslight = df_vars["MEDIANSLIG"].item()
            PGAmoderate = df_vars["MEDIANMODE"].item()
            PGAextensive = df_vars["MEDIANEXTE"].item()
            PGAcomplete = df_vars["MEDIANCOMP"].item()

            # Compute damage probabilities
            # Earthquake damage follows a lognormal cumulative distribution, where small PGA won't cause much damage
            # but damage increase dramatically as PGA increases (so there is a very rapid transition).

            # log of minPGA/PGAThreshold (threshold read from the table): compute the log ratio
            # Which basically reflects the prob of damage given the min PGA of the earthquake.

            # Then the above ratio is scaled using the inverse of beta
            # Larger beta means more uncertainty (each building of this type may have different damage thresholds)
            # So those with larger beta have more strectched out and smooth curves, not that all buildings fall at the very similar threshold.
            
            # PSlight: probability that the given building type will at least experience slight damage.
            Pslight = norm.cdf((1/Bslight)*np.log(minPGA/PGAslight))
            Pmoderate = norm.cdf((1/Bmoderate)*np.log(minPGA/PGAmoderate))
            Pextensive = norm.cdf((1/Bextensive)*np.log(minPGA/PGAextensive))
            Pcomplete = norm.cdf((1/Bcomplete)*np.log(minPGA/PGAcomplete))

            # Estimate cumulative  number of bildings with certain levels of damage
            numSlight = df[BLDG_TYPE].item() * Pslight
            numModerate = numSlight * Pmoderate
            numExtensive = numModerate * Pextensive
            numComplete = numExtensive * Pcomplete

            # Get number of building for each category (subtract off the amount counted under other categories).
            numSlight = numSlight - numModerate
            numModerate = numModerate - numExtensive
            numExtensive = numExtensive - numComplete

            df["Slight"] += numSlight
            df["Moderate"] += numModerate
            df["Extensive"] += numExtensive
            df["Complete"] += numComplete

        tracts.update(df)

    tracts["Green"] = tracts["Slight"]+tracts["Moderate"]
    tracts["Yellow"] = tracts["Extensive"]
    tracts["Red"] = tracts["Complete"]

    tracts.to_file(os.path.join(eventdir, "TractLevel_DamageAssessmentModel_Output.shp"))

    return



if __name__ == "__main__":
    start_time = time.time()
    main()
    print("--- {} seconds ---".format(time.time() - start_time))
