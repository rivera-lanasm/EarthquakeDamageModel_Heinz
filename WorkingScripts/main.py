import o1_Earthquake_ShakeMap_Download
#import o2_Earthquake_ShakeMap_Into_CensusGeographies

def main():
    new_events = o1_Earthquake_ShakeMap_Download.check_for_shakemaps()
    for event in new_events:
        print(event)
    return

if __name__ == "__main__":
    main()

