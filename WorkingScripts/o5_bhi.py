import geopandas as gpd
import pandas as pd
import numpy as np

"""

- utility loss as a user parameter --> HOW DO WE PHRASE THIS
    - low --> UL = .25
    - medium --> UL = .5
    - high --> UL = .75

"""

if __name__ == "__main__":

    # step 0 - import population from census 

    # step 1 - read results from o4
        # number of damaged 
    df = gpd.read_file("Data/o4_results.gpkg")
    for c in df.columns:
        print(c)
    print(df)


