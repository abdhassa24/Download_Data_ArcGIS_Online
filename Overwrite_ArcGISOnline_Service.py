import urllib.request, json
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from arcgis.features import FeatureLayer
import arcpy
from datetime import datetime, timedelta
import logging


log_file = "Log file location"

logging.basicConfig(filename=log_file, filemode='w', level=logging.WARNING,format='%(asctime)s:%(levelname)s:%(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

gis = GIS("organization url","username", "password") #Set up a connection by providing your organization url, username and password
   
def importwiski (urls,info,itemid): #This is a function that takes in three parameters  

  
    with urllib.request.urlopen(urls) as url: #Using the urllib library to download the data from the API into a geojson format  

        data = json.loads(url.read().decode())
        

    with open(info, 'w') as f: 
        json.dump(data,f)

    json_file= info
    
    
    featureLayer_item = gis.content.get(itemid)  #Retrieving the itemid of the ArcGIS Online item


    layer_collection = FeatureLayerCollection.fromitem(featureLayer_item)  #Create a FeatureLayerCollection from an ArcGIS Online item.

    featurelayer = FeatureLayer.fromitem(featureLayer_item, layer_id=0) #Create a FeatureLayer from an ArcGIS Online Item.

    json_data = open(json_file) #Opening the geojson file
    
    json_load = json.load(json_data)
    
    layer_collection.manager.overwrite(json_file) #Overwriting the ArcGIS Online Feature service with the updated geojson file
    

#Calling the function and providing the three parameters which are the api url, the geojson file that was downloaded from the API and the itemid of the ArcGIS Online item
importwiski ("rest endpoint of API","GeoJSON file","itemid")

            
def correctdate(fc): #function that corrects the date because it shows up in ArcGIS Online as an hour ahead and takes daylight savings time to effect
    field = ["datefield"]   #date field
    with arcpy.da.UpdateCursor(fc,field,where_clause="date field IS NOT NULL",) as cursor:   #using update cursor to subtract an hour from the date field
        for row in cursor:
            row[0] += timedelta(hours=-1)
            cursor.updateRow(row)

correctdate("ArcGIS Service Rest Endpoint")
