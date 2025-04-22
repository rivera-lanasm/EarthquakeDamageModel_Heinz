import geopandas as gpd
import pandas as pd
import numpy as np
import os

"""
- utility loss as a user parameter --> HOW DO WE PHRASE THIS
    - low --> UL = .25
    - medium --> UL = .5
    - high --> UL = .75

Estimating Building Habitability
"""

# these can be user parameters
BLDNG_USABILITY = {
"Slight":{"FU": 1, "PU": 0, "NU": 0},
"Moderate":{"FU": 0.87, "PU": 0.13, "NU": 0},
"Extensive":{"FU": 0.25, "PU": 0.5 , "NU": 0.25},
"Complete":{"FU": 0, "PU": 0.02, "NU": 0.98}
    }

# these can be user parameters
# UL_SEVERITY = {
#     "power":{"low":[0,.2], "medium":.3, "high":.6},
#     "water":{"low":.1, "medium":.2, "high":.4},
#     }
    # FU_NH --> 50 --> (10%, 10%, 5%) --> 10%
UL_SEVERITY = {
    "low": {"FU":[0,0.05], "PU": [0.05,0.1]}, # fully usable (0 - 5% non habitable), partially usable (5 - 10%) 
    "medium":{"FU": [0,.1], "PU": [.3,.5]},
    "high":{"FU": [.1,.3], "PU": [.6, .8]}
    }


def tract_damage_lvl(damage_dist):
    """
    match building damage distribution to "low", "med", "high"
    damage_dist -> {"Slight":0.25,
                    "Moderate":0.25,
                    "Extreme":0.25,
                    "Complete":0.25}
    https://docs.google.com/document/d/1Hk4eNn4lFpUYWKAIq8quMi7sOEfdJqGWpIZLmAes-Ec/edit?tab=t.0
    
    destroyed --> complete
    major damage --> moderate, extreme
    """
    destroyed = damage_dist["perc_complete"]
    major = damage_dist["perc_extreme"] # damage_dist["perc_moderate"] 
    if (destroyed > 0.34) | (major > 0.34):
        return "high"
    elif ((destroyed <= 0.34) & (destroyed > 0.1)) | \
        ((major <= 0.34) & (major > 0.15)):
        return "medium"
    else:
        return "low"


def process_bhi(df, parent_dir):

    # ==================================
    # step 0 - import population from census, join
        # source: https://data.census.gov/table/DECENNIALPL2020.P1?t=Populations+and+People&g=040XX00US06$1400000
    pop_path = os.path.join(parent_dir, "Data", "CA_DECENNIALPL2020.csv")
    pop_data = pd.read_csv(pop_path)
    # print(pop_data.head())
    pop_data = pop_data.iloc[1:].reset_index(drop=True)[["GEO_ID", "NAME", "P1_001N"]]
    pop_data["GEO_ID"] = pop_data["GEO_ID"].str.replace("1400000US", "", regex=False)
    
    # ==================================
    # step 1 - read results from o4
    # df = gpd.read_file("Data/o4_results.gpkg")

    # get % buildings in each category 
    df["perc_slight"] = df["Total_Num_Building_Slight"]/df["Total_Num_Building"]
    df["perc_moderate"] = df["Total_Num_Building_Moderate"]/df["Total_Num_Building"]
    df["perc_extreme"] = df["Total_Num_Building_Extensive"]/df["Total_Num_Building"]
    df["perc_complete"] = df["Total_Num_Building_Complete"]/df["Total_Num_Building"]

    # Apply tract_damage_lvl --> utility services
    df["risk_level"] = df[["perc_slight", "perc_moderate", 
                           "perc_extreme", "perc_complete"]].apply(
                                lambda row: tract_damage_lvl(row.to_dict()), axis=1)

    # num_FU
    df["num_FU"] = df["Total_Num_Building_Slight"].apply(lambda x: BLDNG_USABILITY["Slight"]["FU"]*x) +\
                   df["Total_Num_Building_Moderate"].apply(lambda x: BLDNG_USABILITY["Moderate"]["FU"]*x) +\
                   df["Total_Num_Building_Extensive"].apply(lambda x: BLDNG_USABILITY["Extensive"]["FU"]*x) +\
                   df["Total_Num_Building_Complete"].apply(lambda x: BLDNG_USABILITY["Complete"]["FU"]*x)
    # perc_FU_NH_low
    df["perc_FU_NH_low"] = df.apply(lambda row: UL_SEVERITY[row['risk_level']]["FU"][0], axis=1)
    df["perc_FU_NH_high"] = df.apply(lambda row: UL_SEVERITY[row['risk_level']]["FU"][1], axis=1)

    # num_PU
    df["num_PU"] = df["Total_Num_Building_Slight"].apply(lambda x: BLDNG_USABILITY["Slight"]["PU"]*x) +\
                   df["Total_Num_Building_Moderate"].apply(lambda x: BLDNG_USABILITY["Moderate"]["PU"]*x) +\
                   df["Total_Num_Building_Extensive"].apply(lambda x: BLDNG_USABILITY["Extensive"]["PU"]*x) +\
                   df["Total_Num_Building_Complete"].apply(lambda x: BLDNG_USABILITY["Complete"]["PU"]*x)

    # perc_PU_NH
    df["perc_PU_NH_low"] = df.apply(lambda row: UL_SEVERITY[row['risk_level']]["PU"][0], axis=1)
    df["perc_PU_NH_high"] = df.apply(lambda row: UL_SEVERITY[row['risk_level']]["PU"][1], axis=1)

    # num_NU
    df["num_NU"] = df["Total_Num_Building_Slight"].apply(lambda x: BLDNG_USABILITY["Slight"]["NU"]*x) +\
                   df["Total_Num_Building_Moderate"].apply(lambda x: BLDNG_USABILITY["Moderate"]["NU"]*x) +\
                   df["Total_Num_Building_Extensive"].apply(lambda x: BLDNG_USABILITY["Extensive"]["NU"]*x) +\
                   df["Total_Num_Building_Complete"].apply(lambda x: BLDNG_USABILITY["Complete"]["NU"]*x)

    # BHI_factor = (num_FU*perc_FU_NH + num_PU*perc_PU_NH + num_NU) / N
    df["BHI_factor_low"] = (df["num_FU"]*df["perc_FU_NH_low"] + df["num_PU"]*df["perc_PU_NH_low"] + df["num_NU"])/df["Total_Num_Building"]
    df["BHI_factor_high"] = (df["num_FU"]*df["perc_FU_NH_high"] + df["num_PU"]*df["perc_PU_NH_high"] + df["num_NU"])/df["Total_Num_Building"]

    # apply residential factor
    # resi_df = pd.read_csv("/home/rivlanm/cmu/EarthquakeDamageModel_Heinz/Data/building_data_csv/CA_building_data.csv")

    # (.5)*(.5) = .25
    

    # join census population data
    final_col_set = ["GEOID", "max_intensity",
                     "Total_Num_Building",
                     "Total_Num_Building_Slight", "Total_Num_Building_Moderate", 
                     "Total_Num_Building_Extensive", "Total_Num_Building_Complete",
                     "risk_level", 
                     "num_FU", "perc_FU_NH_low", "perc_FU_NH_high",
                     "num_PU", "perc_PU_NH_low", "perc_PU_NH_high",
                     "num_NU",
                     "BHI_factor_low", "BHI_factor_high"]

    df = df[final_col_set].sort_values(by=["max_intensity"], ascending=False).reset_index(drop=True)
    df['GEOID'] = np.where(df['GEOID'].str.len() == 11, df['GEOID'], "0"+df['GEOID'])
    
    # merge pop data
    df = df.merge(pop_data[["GEO_ID", "P1_001N"]], how="inner", left_on="GEOID", right_on="GEO_ID")
    df = df.drop(columns=["GEO_ID"])
    df = df.rename(columns={"P1_001N":"population"})

    df["denominator"] = df["Total_Num_Building"]

    return df

# if __name__ == "__main__":

#     df = process_bhi()


#     df["population"] = df["population"].astype(int)
#     df["shelter_seeking_low"] = df["BHI_factor_low"]*df["population"]
#     df["shelter_seeking_high"] = df["BHI_factor_high"]*df["population"]
#     cols = ["GEOID", "max_intensity", "population", "Total_Num_Building", "risk_level",
#             "BHI_factor_low", #"BHI_factor_high",
#             "shelter_seeking_low", #"shelter_seeking_high",
#             "Total_Num_Building_Slight", "Total_Num_Building_Moderate", 
#              "Total_Num_Building_Extensive", "Total_Num_Building_Complete"]

#     df = df[cols]

#     df["BHI_factor_low"] = df["BHI_factor_low"].apply(lambda x: round(x,4))
#     df["shelter_seeking_low"] = df["shelter_seeking_low"].apply(lambda x: round(x,4))
    
#     # BHI (census) = BHI_factor * census tract population --> number of people in census tract with non-habitable housing
#     df.to_csv("Data/bhi_output.csv", index=False)
    
    #pop_data = pd.read_csv("Data/CA_DECENNIALPL2020.csv")

    # SVI --> [0,1] (higher is more vulnerable)


    # 100, SVI = .5 --> 50 





