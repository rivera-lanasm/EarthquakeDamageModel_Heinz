"""
File Description Added by Meriem

This script offers two main modes:
1.  Testing mode: 
        - Uses either Napa 2014 or Idaho 2017 as case studies (customizable)
        - Processes 
                - (1) Census data [using shakemap_into_census_geo() from script o2_Earthquake_ShakeMap_Into_CensusGeographies.py ]; 
                - (2) Building Outlines [using shakemap_get_bldgs() from o3_Earthquake_GetBldgCentroids.py script]; 
                - (3) and generates trace-level damage assessment model for each event in the incident [using main() from o4_TractLevel_DamageAssessmentModel.py)

2. Non Testing mode: Look for new eartquake events [using check_for_shakemaps() from o1_Earthquake_ShakeMap_Download.py]
"""
import os
import time
        
import o1_Earthquake_ShakeMap_Download
import o2_Earthquake_ShakeMap_Into_CensusGeographies
import o3_Earthquake_GetBldgCentroids
import o4_TractLevel_DamageAssessmentModel
import config


def main(testingmode = False):
    if not testingmode:
        # if not in testing mode, look for real new shakemaps
        new_events = o1_Earthquake_ShakeMap_Download.check_for_shakemaps()
        # new events should be a list of newly downloaded earthquake event folders


    else:
        # if testing mode, use the napa 2014 shakemap
        print('testing mode')
        # new_events = [config.NapaEventDir]
        new_events = [config.IdahoEventDir]

    for event in new_events:
        print('\nCensus Data Processing for: ', event)
        o2_Earthquake_ShakeMap_Into_CensusGeographies.shakemap_into_census_geo(eventdir = event)

        print('\nGathering Building Outlines for: ', event)
        ORNL_LB_bldgs = o3_Earthquake_GetBldgCentroids.shakemap_get_bldgs(eventdir = event)

        print('\nRunning Tract-Level Damage Assessment Model for: ', event)
        o4_TractLevel_DamageAssessmentModel.main(eventdir = event)

    return


if __name__ == "__main__":
    start_time = time.time()
    main(testingmode=True)
    print("--- {} seconds ---".format(time.time() - start_time))

