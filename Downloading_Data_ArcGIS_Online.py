import time
from datetime import timedelta
import os
import zipfile
import arcgis.gis
from zipfile import ZipFile
import arcpy
from sys import argv
import shutil
import logging


log_file = "Log file location"

logging.basicConfig(filename=log_file, filemode='w', level=logging.WARNING,format='%(asctime)s:%(levelname)s:%(message)s',datefmt='%m/%d/%Y %I:%M:%S %p')

start_time = time.monotonic()

gis = arcgis.GIS("organization url", "username", "password") #Set up a connection by providing your organization url, username and password

arcpy.env.workspace = "SDE database connection"  #Set workspace to the sde database

def downloaddata(outputFolder,boolean,item_id, filegdb): # This is a function that takes three parameters
    AGOLitem = gis.content.get(item_id)  #Retrieve item id from my contents
    params = {"editorTrackingInfo" : {"enableEditorTracking":boolean, "preserveEditUsersAndTimestamps":boolean}} #if layer has editor tracking enabled it will preserve it
    print ("Exporting Hosted Feature Layer...")
    AGOLitem.export(filegdb,'File Geodatabase',parameters=params,wait=True) #Export the data as a file geodatabase
    time.sleep(10)   #add 10 seconds delay to allow export to complete

    search_fgb = gis.content.search(filegdb) #find the CSV in ArcGIS online
    fgb_item_id = search_fgb[0].id
    fgb = gis.content.get(fgb_item_id)
    fgb.download(save_path=outputFolder) #download CSV from ArcGIS Online to your computer

    print ("Zipping exported geodatabase for download...")

    zipfullpath=os.path.join(outputFolder,filegdb+".zip") 
    zf = ZipFile(os.path.join(outputFolder,filegdb+ ".zip"))
     
    print ("Extracting zipped file to geodatabase...")
    zf.extractall(path=os.path.join(outputFolder)) #note: File gdb is completely random)
   

    with ZipFile(zipfullpath, "r") as f:  #get names of files in zipped folder.
        info =f.namelist()
        for name in info:
            if ".gdb/" in name:
                global gdbname
                gdbname=str(name).split("/", 1)[0]
                
    print ("Exported geodatabase is named: "+ gdbname)
    
    '''delete zipped file in ArcGIS Online '''
    del zf #deletes the zf vairable so the lock file goes away
    print("Deleting "+ os.path.join(outputFolder,filegdb+".zip"))
    os.remove(zipfullpath) #deletes actual zipped file on your computer

    '''deleting hosted File Geodatabase'''
    print("Deleting "+fgb.title+"("+fgb.type+")"+" from ArcGIS Online...")  
    fgb.delete() #This will delete CSV in ArcGIS Online 
    return downloaddata

#Calling function and providing the three parameters which is the output folder name, itemid and the file gdb
downloaddata("output folder name",True,"itemid","file gdb")

def rename_file(folder,name):
    os.chdir(folder)
    files = os.listdir(folder)
    os.rename(files[0],name)

rename_file("output folder name","new name of file gdb that was downloaded")


def truncatedrows(rows):
     edit = arcpy.da.Editor(r"SDE Database connection")

     edit.startEditing(False, True) 

     arcpy.TruncateTable_management(rows)

     edit.stopEditing(True)
       
truncatedrows("SDE Feature Class")

def importsde(fc,floodwatch): #function to append the updated rows to the various new site feature class and attachment table
    Table = fc
    Updated_rows= floodwatch
    with arcpy.EnvManager(preserveGlobalIds=True): #Using the append geoprocessing tools to add the updated rows to the various feature classes
        arcpy.management.Append(inputs=[Table], target=Updated_rows, schema_type="No_Test",field_mapping="", subtype="", expression="")
    
  
#calling the function with the parameters 
importsde("ArcGIS Online Feature Class","SDE Feature Class")

#function to change the timezone from utc to the local timezone
def timezone(table,timefield,timezone,outputtime,outputzone,inputdst,outputdst): 
    in_table = table
    input_time_field = timefield
    input_time_zone = timezone
    output_time_field = outputtime
    output_time_zone = outputzone
    input_dst = inputdst
    output_dst = outputdst

    arcpy.ConvertTimeZone_management(in_table,input_time_field,input_time_zone,output_time_field,output_time_zone,input_dst,output_dst) #Change timezone from utc to our local time zone using the convert time zone geoprocessing tool

timezone("SDE Feature Class","created_date","UTC","date_created","Eastern_Standard_Time","INPUT_ADJUSTED_FOR_DST","OUTPUT_ADJUSTED_FOR_DST")
timezone("SDE Feature Class","last_edited_date","UTC","edited_date","Eastern_Standard_Time","INPUT_ADJUSTED_FOR_DST","OUTPUT_ADJUSTED_FOR_DST")

def deletefilegdb (folder):
    shutil.rmtree(folder)

deletefilegdb("Delete File GDB from computer")

end_time = time.monotonic()

