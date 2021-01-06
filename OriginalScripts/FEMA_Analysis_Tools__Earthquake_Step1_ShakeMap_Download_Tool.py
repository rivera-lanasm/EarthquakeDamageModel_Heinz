#-------------------------------------------------------------------------------
# Name:        ShakeMap_Download
# Purpose:      Check USGS database of "Significant Events" that have occurred
#               in the last week, if any events have been added, download and
#               extract ShakeMap shapefiles to a specified folder.
#
# Author:      Madeline Jones
#
# Created:     26/04/2017
#
#-------------------------------------------------------------------------------

# USGS ShakeMap Import Script - modified from:
#    https://gist.github.com/mhearne-usgs/6b040c0b423b7d03f4b9
# Live feeds are found here:
#    http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php

arcpy.AddMessage('Running..')

# Imports
import arcpy
try:
    from urllib2 import urlopen
except:
    from urllib.request import urlopen
import json
import sys
import os.path
import zipfile
import StringIO
import datetime

## uncomment these when inside a FEMA network
#os.environ["HTTP_PROXY"] = "http://proxy.apps.dhs.gov:80"
#os.environ["HTTPS_PROXY"] = "http://proxy.apps.dhs.gov:80"

# Set file path to save ShakeMap zip files to
#FilePath=r"C:\Users\madel\Desktop\ShakeMapTest"
#FilePath=r"C:\ShakeMapTest"
FilePath=arcpy.GetParameterAsText(0)

if not os.path.isdir(FilePath):
        os.mkdir(FilePath)

# Create variables
pnt = arcpy.Point()

FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson' #Significant Events - 1 week
#FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_hour.geojson' #1 hour M4.5+
#FEEDURL = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/4.5_day.geojson' #1 day M4.5+

# Get the list of event IDs in the current feed
fh = urlopen(FEEDURL) #open a URL connection to the event feed.
data = fh.read() #read all of the data from that URL into a string
fh.close()
jdict = json.loads(data) #Parse that data using the stdlib json module.  This turns into a Python dictionary.

#arcpy.AddMessage('Running 2')

# Create list of files in current folder
FileList = os.listdir(FilePath)

# Check to see if any new events have been added. If so, run code. If not, break and exit.
eqIDlist=[earthquake['id'] for earthquake in jdict['features']]


for earthquake in jdict['features']: #jdict['features'] is the list of events
    eventid = earthquake['id']

    #if earthquake['id'] == eventid:
    #for earthquake['id'] in earthquake['id']:
    eventurl = earthquake['properties']['detail'] #get the event-specific URL
    fh = urlopen(eventurl)
    data = fh.read() #read event data into a string
    fh.close()
    jdict2 = json.loads(data) #and parse using json module as before
    if 'shakemap' not in jdict2['properties']['products'].keys():
        arcpy.AddMessage('Event %s does not have a ShakeMap product associated with it. Exiting.')
        sys.exit(1)
    shakemap = jdict2['properties']['products']['shakemap'][0] #get the first shakemap associated with the event
    shapezipurl = shakemap['contents']['download/shape.zip']['url'] #get the download url for the shape zipfile.
    epicenterurl = shakemap['contents']['download/epicenter.kmz']['url']

## EXTRACT SHAKEMAP ZIP FILE IN NEW FOLDER

    #Here, read the binary zipfile into a string
    fh = urlopen(shapezipurl)
    data = fh.read()
    fh.close()

    #Create a StringIO object, which behaves like a file
    stringbuf = StringIO.StringIO(data)
    eventdir = "{}\{}".format(FilePath,str(eventid))

    # Creates a new folder (called the eventid) if it does not already exist
    if not os.path.isdir(eventdir):
        os.mkdir(eventdir)
        arcpy.AddMessage("New EventID: {}".format(eventid))

        #Create a StringIO object, which behaves like a file
        stringbuf = StringIO.StringIO(data)
        eventdir = "{}\{}".format(FilePath,str(eventid))

        # Create a ZipFile object, instantiated with our file-like StringIO object.
        # Extract all of the data from that StringIO object into files in the provided output directory.
        myzip = zipfile.ZipFile(stringbuf,'r',zipfile.ZIP_DEFLATED)
        myzip.extractall(eventdir)
        myzip.close()
        stringbuf.close()

        # Create feature class of earthquake info
        epiX = earthquake['geometry']['coordinates'][0]
        epiY = earthquake['geometry']['coordinates'][1]
        depth = earthquake['geometry']['coordinates'][2]
        title = str(earthquake['properties']['title'])
        mag = earthquake['properties']['mag']
        time = str(earthquake['properties']['time'])
        time_ = datetime.datetime.fromtimestamp(int(time[:-3])).strftime('%c')
        place = str(earthquake['properties']['place'])
        #felt = earthquake['properties']['felt']
        url = str(earthquake['properties']['url'])
        eventid = str(eventid)
        status = str(earthquake['properties']['status'])
        updated = str(earthquake['properties']['updated'])
        updated_ = datetime.datetime.fromtimestamp(int(updated[:-3])).strftime('%c')

        f = open(eventdir+"\\eventInfo.txt","w+")
        f.write("{}\r\n{}\r\n".format(status,updated))
        f.close()
        
        COMBO = (title,mag,time,place,depth,url,eventid)
        arcpy.AddMessage(COMBO)
        
        # Update empty point with epicenter lat/long
        pnt.X = epiX
        pnt.Y = epiY

        # Add fields to Epicenter shapefile
        arcpy.CreateFeatureclass_management(eventdir,"Epicenter","POINT","","","",4326)
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Title","TEXT","","","","Event")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Mag","FLOAT","","","","Magnitude")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Date_Time","TEXT","","","","Date/Time")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Place","TEXT","","","","Place")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Depth_km","FLOAT","","","","Depth (km)")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Url","TEXT","","","","Url")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"EventID","TEXT","","","","Event ID")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Status","TEXT","","","","Status")
        arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Updated","TEXT","","","","Updated")

        # Add earthquake info to Epicenter attribute table
        curs = arcpy.da.InsertCursor("{}\Epicenter.shp".format(eventdir),["Title","Mag","Date_Time","Place","Depth_km","Url","EventID","Status","Updated"])
        curs.insertRow((title,mag,time_,place,depth,url,eventid,status,updated_))
        del curs

        



        # Add XY point data to Epicenter shapefile
        with arcpy.da.UpdateCursor("{}\Epicenter.shp".format(eventdir),"SHAPE@XY") as cursor:
            for eq in cursor:
                eq[0]=pnt
                cursor.updateRow(eq)

        filelist = os.listdir(eventdir)
        arcpy.AddMessage('Extracted {} ShakeMap files to {}'.format(len(filelist),eventdir))

    else:


        # go into folder and read former status and update time
        f = open(eventdir+"\\eventInfo.txt","r")
        oldstatus = f.readline()
        oldstatus = oldstatus.rstrip()
        oldupdated = f.readline()
        oldupdated = oldupdated.rstrip()
        f.close()


        status = str(earthquake['properties']['status'])
        updated = str(earthquake['properties']['updated'])

        # check to see if new dataset has been updated or has a new status
        t=1
        if status == oldstatus:
            t=0
    
        if int(updated) > int(oldupdated) or t==1:

            # delete all old files
            for root, dirs, files in os.walk(eventdir):
                for filename in files:
                    os.remove(eventdir + "\\" + filename)

            arcpy.AddMessage("ShakeMap files for {} have been updated. Old files are deleted. New files are unzipping.".format(eventid))


            myzip = zipfile.ZipFile(stringbuf,'r',zipfile.ZIP_DEFLATED)
            myzip.extractall(eventdir)
            myzip.close()
            stringbuf.close()

            # Create feature class of earthquake info
            epiX = earthquake['geometry']['coordinates'][0]
            epiY = earthquake['geometry']['coordinates'][1]
            depth = earthquake['geometry']['coordinates'][2]
            title = str(earthquake['properties']['title'])
            mag = earthquake['properties']['mag']
            time = str(earthquake['properties']['time'])
            place = str(earthquake['properties']['place'])
            #felt = earthquake['properties']['felt']
            url = str(earthquake['properties']['url'])
            eventid = str(eventid)
            status = str(earthquake['properties']['status'])
            updated = str(earthquake['properties']['updated'])

            f = open(eventdir+"\\eventInfo.txt","w+")
            f.write("{}\r\n{}\r\n".format(status,updated))
            f.close()
                
            COMBO = (title,mag,time,place,depth,url,eventid)
            arcpy.AddMessage(COMBO)
            
            # Update empty point with epicenter lat/long
            pnt.X = epiX
            pnt.Y = epiY

            # Add fields to Epicenter shapefile
            arcpy.CreateFeatureclass_management(eventdir,"Epicenter","POINT","","","",4326)
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Title","TEXT","","","","Event")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Mag","FLOAT","","","","Magnitude")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Date_Time","TEXT","","","","Date/Time")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Place","TEXT","","","","Place")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Depth_km","FLOAT","","","","Depth (km)")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Url","TEXT","","","","Url")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"EventID","TEXT","","","","Event ID")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Status","TEXT","","","","Status")
            arcpy.AddField_management("{}\Epicenter.shp".format(eventdir),"Updated","TEXT","","","","Updated")

            # Add earthquake info to Epicenter attribute table
            curs = arcpy.da.InsertCursor("{}\Epicenter.shp".format(eventdir),["Title","Mag","Date_Time","Place","Depth_km","Url","EventID","Status","Updated"])
            curs.insertRow((title,mag,time,place,depth,url,eventid,status,updated))
            del curs


            # Add XY point data to Epicenter shapefile
            with arcpy.da.UpdateCursor("{}\Epicenter.shp".format(eventdir),"SHAPE@XY") as cursor:
                for eq in cursor:
                    eq[0]=pnt
                    cursor.updateRow(eq)

            filelist = os.listdir(eventdir)
            arcpy.AddMessage('Extracted {} ShakeMap files to {}'.format(len(filelist),eventdir))


        else:
            
            arcpy.AddMessage("ShakeMap files for {} already exist and have not been updated.".format(eventid))

arcpy.AddMessage("Completed.")


