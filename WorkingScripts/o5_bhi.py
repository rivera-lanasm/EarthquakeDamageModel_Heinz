import geopandas as gpd
import pandas as pd
import numpy as np

"""

- utility loss as a user parameter --> HOW DO WE PHRASE THIS
    - low --> UL = .25
    - medium --> UL = .5
    - high --> UL = .75

Estimating Building Habitability

    
"""

# these can be user parameters
BLDNG_USABILITY = {
"Slight":{"FU": 0.87, "PU": 0.13, "NU": 0},
"Moderate":{"FU": 0.87, "PU": 0.13, "NU": 0},
"Extreme":{"FU": 0.22, "PU": 0.25 , "NU": 0.53},
"Complete":{"FU": 0, "PU": 0.02, "NU": 0.98}
    }

# these can be user parameters
UL_SEVERITY = {
    "power":{"low":.1, "medium":.3, "high":.6},
    "water":{"low":.1, "medium":.2, "high":.4},
    "waste":{"low":.05, "medium":.3, "high":.6},
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
    major = damage_dist["perc_moderate"] + damage_dist["perc_extreme"]
    if (destroyed > 0.34) | (major > 0.34):
        return "high"
    elif ((destroyed <= 0.34) & (destroyed > 0.1)) | \
        ((major <= 0.34) & (major > 0.15)):
        return "medium"
    else:
        return "low"

def num_FU():

    return 

def num_PU():
    
    return 

def num_NU():

    return

def perc_NH_FU(damage_lvl, w_power, w_water, w_waste):
    """
    https://docs.google.com/document/d/1Hk4eNn4lFpUYWKAIq8quMi7sOEfdJqGWpIZLmAes-Ec/edit?tab=t.0
    """


    return 


if __name__ == "__main__":

    # ==================================
    # step 0 - import population from census, join
    pop_data = pd.read_csv("Data/CA_DECENNIALPL2020.csv")
    print(pop_data.head())

    # ==================================
    # step 1 - read results from o4
    df = gpd.read_file("Data/o4_results.gpkg")
    for c in df.columns:
        print(c)
    print(df)

    # get % buildings in each category 
    df["perc_slight"] = df["Total_Num_Building_Slight"]/df["Total_Num_Building"]
    df["perc_moderate"] = df["Total_Num_Building_Moderate"]/df["Total_Num_Building"]
    df["perc_extreme"] = df["Total_Num_Building_Extensive"]/df["Total_Num_Building"]
    df["perc_complete"] = df["Total_Num_Building_Complete"]/df["Total_Num_Building"]

    # Apply tract_damage_lvl
    df["risk_level"] = df[["perc_slight", "perc_moderate", 
                           "perc_extreme", "perc_complete"]].apply(
                                lambda row: tract_damage_lvl(row.to_dict()), axis=1)

    # num_FU

    # perc_FU_NH

    # num_PU

    # perc_PU_NH

    # num_NU

    # BHI_factor = (num_FU*perc_FU_NH + num_PU*perc_PU_NH + num_NU) / N
    # BHI = BHI_factor * census population 
