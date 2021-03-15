import os
import time
        
import o1_Earthquake_ShakeMap_Download
import o2_Earthquake_ShakeMap_Into_CensusGeographies
import o3_Earthquake_GetBldgCentroids
import o4_TractLevel_DamageAssessmentModel


def main(testingmode = False):
    if not testingmode:
        # if not in testing mode, look for real new shakemaps
        new_events = o1_Earthquake_ShakeMap_Download.check_for_shakemaps()
        # new events should be a list of newly downloaded earthquake event folders


    else:
        # if testing mode, use the napa 2014 shakemap
        print('testing mode')
        # new_events = [r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\napa2014shakemap_fortesting"]
        new_events = [r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\idaho2017shakemap_fortesting"]

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
    main(testingmode=False)
    print("--- {} seconds ---".format(time.time() - start_time))

