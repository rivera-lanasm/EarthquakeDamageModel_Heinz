import os
        
import o1_Earthquake_ShakeMap_Download
import o2_Earthquake_ShakeMap_Into_CensusGeographies

def main(testingmode = False):
    if not testingmode:
        # if not in testing mode, look for real new shakemaps
        new_events = o1_Earthquake_ShakeMap_Download.check_for_shakemaps()
        # new events should be a list of newly downloaded earthquake event folders



    else:
        # if testing mode, use the napa 2014 shakemap
        print('testing mode')
        new_events = [r"C:\Projects\FEMA\EarthquakeModel\ShakeMaps\napa2014shakemap_fortesting"]

    for event in new_events:
        print('\nCensus Data Processing for: ', event)
        o2_Earthquake_ShakeMap_Into_CensusGeographies.shakemap_into_census_geo(event)

    return


if __name__ == "__main__":
    main(testingmode=False)

