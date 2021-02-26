import fiona
import geopandas as gp
import pandas as pd
from scipy.stats import norm
import matplotlib.pyplot as plt
import numpy as np

# Import Spreadsheet with Hazus Building Type Breakdown per Tract
bldg_percentages_by_tract_csv = r"C:\Projects\FEMA\EarthquakeModel\tables\Building_Percentages_Per_Tract_ALLSTATES.csv"
bldg_percentages_by_tract_df = pd.read_csv(bldg_percentages_by_tract_csv)

#add leading zeroes to FIPS codes that do not have leading zeroes
for fips in bldg_percentages_by_tract_df["Tract_str"].unique():
    if len(fips) == 11:
        None
    elif len(fips) == 10:
        # add leading zero to fips string
        newfips = "0" + fips
        idx = bldg_percentages_by_tract_df[bldg_percentages_by_tract_df["Tract_str"]==fips]["Tract_str"].index
        bldg_percentages_by_tract_df.loc[idx, "Tract_str"] = newfips


def main(tracts_layer = "census_tract_max_mmi_pga_pgv", bldgs_layer = "ORNL_LB_bldgs", gdb = r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\napa2014shakemap_fortesting\eqmodel_outputs.gdb"):


    tracts = gp.read_file(gdb, layer = tracts_layer)
    tract_FIPS_list = tracts["FIPS"].unique()

    bldgs = gp.read_file(gdb, layer = bldgs_layer)


    for FIPS in tract_FIPS_list:
        subset = tracts[tracts["FIPS"] == FIPS]




    # Get subset of Hazus Bldg Type Breakdown for Tract
    bldg_percentages_by_tract_df["Tract_str"] = bldg_percentages_by_tract_df["Tract"].apply(str)
    subset_bldgpcts = bldg_percentages_by_tract_df[bldg_percentages_by_tract_df["Tract_str"]==FIPS[1:]]
    subset_bldgpcts


    # In[96]:


    df = subset[["FIPS", "max_MMI", "max_PGA", "max_PGV", "min_PGA", "MS_Bldg_Count", "geometry"]]
    df


    # In[97]:


    subset_bldgpcts.columns
    new_cols = ['W1', 'W2', 'S1L', 'S1M', 'S1H', 'S2L', 'S2M', 'S2H', 'S3',
                'S4L', 'S4M', 'S4H', 'S5L', 'S5M', 'S5H', 'C1L', 'C1M', 'C1H', 'C2L',
                'C2M', 'C2H', 'C3L', 'C3M', 'C3H', 'PC1', 'PC2L', 'PC2M', 'PC2H',
                'RM1L', 'RM1M', 'RM2L', 'RM2M', 'RM2H', 'URML', 'URMM', 'MH']


    # In[98]:


    for col in new_cols:
        df[col] = len(ms_bldgs)*subset_bldgpcts[col].iloc[0]
    df


    # In[99]:


    maxPGA = df["max_PGA"].item()
    minPGA = df["min_PGA"].item()
    print("Max PGA: {} g".format(maxPGA))
    print("Min PGA: {} g".format(minPGA))


    # In[100]:


    # Import Damage Function Variables Spreadsheet
    dmgfvars = "DamageFunctionVariables.csv"


    # In[101]:


    dmgfvarsDF = pd.read_csv(dmgfvars)
    dmgfvarsDF = dmgfvarsDF.drop('Unnamed: 0', axis=1)


    # In[102]:


    dmgfvarsDF.head(10)


    # In[103]:


    dmgfvarsDF[dmgfvarsDF["BLDG_TYPE"]=="W1"]


    # In[104]:


    xrange = np.arange(0.0,3.0,0.1) #PGA
    yrange = np.arange(0.0,1.0,0.1) #probability of meeting or exceeding a certain damage state


    # In[105]:


    df["Slight"] = 0
    df["Moderate"] = 0
    df["Extensive"] = 0
    df["Complete"] = 0
    df


    # In[61]:


    # This runs through each building type, assuming High Code but dropping to Medium, Low or Pre-Code depending
    # on what variables are available, then grabs the variables associated with that Building Type + Code

    # Then, plots the damage function curve and based on the Min or Max PGA, estimates the probability of damage
    # for that structure type. The probabilities are then multiplied by the number of structures in the tract.


    list_bldgtypes = dmgfvarsDF["BLDG_TYPE"].unique()

    T = 0
    fig, axs = plt.subplots(6, 6)
    xax=0
    yax=0

    for BLDG_TYPE in list_bldgtypes:
        if yax == 6:
            yax = 0
            xax += 1

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

        print("\n", BLDG_TYPE, " ", seiscode)

        i = df_vars.index
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

        print("Variables for equation: \n")
        print(PGAslight, PGAmoderate, PGAextensive, PGAcomplete)

        slight = norm.cdf((1/Bslight)*np.log(xrange/PGAslight))
        moderate = norm.cdf((1/Bmoderate)*np.log(xrange/PGAmoderate))
        extensive = norm.cdf((1/Bextensive)*np.log(xrange/PGAextensive))
        complete = norm.cdf((1/Bcomplete)*np.log(xrange/PGAcomplete))


        axs[xax, yax].plot(xrange, slight,'b-', lw=1, alpha=1, label='slight')
        axs[xax, yax].plot(xrange, moderate,'g-', lw=1, alpha=1, label='moderate')
        axs[xax, yax].plot(xrange, extensive,'orange', lw=1, alpha=1, label='extensive')
        axs[xax, yax].plot(xrange, complete,'r-', lw=1, alpha=1, label='complete')
        axs[xax, yax].set_title('{}'.format(BLDG_TYPE + seiscode))


        Pslight = norm.cdf((1/Bslight)*np.log(minPGA/PGAslight))
        Pmoderate = norm.cdf((1/Bmoderate)*np.log(minPGA/PGAmoderate))
        Pextensive = norm.cdf((1/Bextensive)*np.log(minPGA/PGAextensive))
        Pcomplete = norm.cdf((1/Bcomplete)*np.log(minPGA/PGAcomplete))

        print("\nProb slight damage: ", Pslight)
        print("Num slight damage: ", df[BLDG_TYPE].item() * Pslight)
        print("Num {} bldgs: ".format(BLDG_TYPE), df[BLDG_TYPE].item())

        print("\nProb complete damage: ", Pcomplete)
        print("Num complete damage: ", df[BLDG_TYPE].item() * Pcomplete)
        print("Num {} bldgs: ".format(BLDG_TYPE), df[BLDG_TYPE].item())

        numSlight = df[BLDG_TYPE].item() * Pslight
        numModerate = numSlight * Pmoderate
        numExtensive = numModerate * Pextensive
        numComplete = numExtensive * Pcomplete

        numSlight = numSlight - numModerate
        numModerate = numModerate - numExtensive
        numExtensive = numExtensive - numComplete

        df["Slight"] += numSlight
        df["Moderate"] += numModerate
        df["Extensive"] += numExtensive
        df["Complete"] += numComplete
        T += 1
        yax += 1

    print(T)




    # In[23]:


    fig.set_size_inches(22,16)
    fig.savefig("damageFunctions", dpi=None, facecolor='w', edgecolor='w',
            orientation='portrait')


    # In[62]:


    df


    # In[ ]:


    698 + 204 + 24 + 0 #minPGA, combined calculations


    #
    # | | RESULTS (from this code) | HAZUS RESULTS | CURRENT PTOLEMY RESULTS |
    # | --- | --- | --- | --- |
    # | Red | 0 | 4 | 0|
    # | Yellow | 24 | 42 | 740|
    # | Green | 903 | 671 | 242 |
    # | No Damage | 1750 | - | 1677|
    #
    #
    #

    # In[ ]:


    ## SCRIPT OUTPUTS
    # Ptolemy MS: Destroyed	0
    # Ptolemy MS: Severe Damage	24
    # Ptolemy MS: Significant Damage	903
    # Ptolemy MS: No Damage	1750


    # In[ ]:


    ## HAZUS RESULTS
    # Hazus: Red Tag	4
    # Hazus: Yellow Tag	42
    # Hazus: Green Tag	671


    # In[ ]:


    ### CURRENT MODEL OUTPUTS
    # Ptolemy MS: Destroyed	0
    # Ptolemy MS: Severe Damage	740
    # Ptolemy MS: Significant Damage	242
    # Ptolemy MS: No Damage	1677




if __name__ == "__main__":
    main()