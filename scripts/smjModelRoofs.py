#smjModelRoofs.py

#purpse:
#model Roofs into 3D Objectd

#Owners
#Susan Jones & Amit Kokje
#Spatial Logic Limited
#Auckland, New Zealand

#sjones@spatiallogic.co.nz
#http://www.spatiallogic.co.nz/

#30 January 2013

#import Modules
import arcpy, string, fpformat, os

#findLength
def findLength(r,b):
    dx=pow(r.X-b.X,2)
    dy=pow(r.Y-b.Y,2)
    dz=pow(r.Z-b.Z,2)
    length=pow(dx+dy+dz,0.5)

    return length

#banner
print("***\nMODEL MULTIPART BUILDINGS\n***")

#datasets
#TODO: Place the Data Sources Here
print("***get Datasets")
gdb=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb"
buildingFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\BuildingFootprints"
structuresFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\Structures"
ridgelinesFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\Ridgelines"

#make Buildings Layer
print("make Buildings Layer")
arcpy.MakeFeatureLayer_management(buildingFc,"buildings1")

#set Environment
arcpy.env.workspace=gdb
arcpy.env.overwriteOutput=1
arcpy.env.outputZFlag="Enabled"

#create Featureclass
descfc=arcpy.Describe(structuresFc)
arcpy.CreateFeatureclass_management (gdb, "Rooves", "POLYLINE", structuresFc, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", descfc.spatialReference)

#insert Recs
print("insert Records")
irecs=arcpy.InsertCursor(gdb+"\\Rooves")

#make Search Cursor for Buildings
arcpy.MakeFeatureLayer_management(ridgelinesFc,"ridgelines1")
n=0
recs=arcpy.SearchCursor("ridgelines1")
print arcpy.GetCount_management("ridgelines1")
rec=recs.next()
while rec:

    #extract Mininun
    minimum=rec.minimum
    z=rec.z
    ridge=rec.shape.getPart(0)

    #make extent
    sql="\"OBJECTID\"="+str(rec.objectid)
    arcpy.MakeFeatureLayer_management("ridgelines1", "ridgelines2", sql)
    arcpy.SelectLayerByLocation_management("buildings1", "CONTAINS", "ridgelines2")
    print "noFeatures:"+str(arcpy.GetCount_management("buildings1"))

    #buildings
    minArea=0
    srecs=arcpy.SearchCursor("buildings1")
    srec=srecs.next()
    while srec:

        #get The Building
        if srec.shape.area>minArea:
            minArea=srec.shape.area
            base=srec.shape.getPart(0)

        #next srec
        srec=srecs.next()

##    #minArea
##    print minArea


    #make Ridge in 3D
    p1=ridge[0]
    p1.Z=z
    p2=ridge[1]
    p2.Z=z
    na=arcpy.Array()
    na.append(p1)
    na.append(p2)
    rl=arcpy.Polyline(na)

    #make And Populate Records
    irec=irecs.newRow()
    irec.shape=rl
    irec.z=z
    irec.minimum=minimum
    irecs.insertRow(irec)
    print("added")
    del na

    #ridge Array
    for r in ridge:
        r.Z=z

        #building Array
        for b in base:
            b.Z=minimum

##            #findLength
##            length=findLength(r,b)
##            print length

            #make And Populate Records
            irec=irecs.newRow()
            seg=arcpy.Array()
            seg.append(r)
            seg.append(b)
            line=arcpy.Polyline(seg)
            irec.shape=seg
            irec.z=z
            irec.minimum=minimum
            irecs.insertRow(irec)

    #add The Base
    irec=irecs.newRow()
    line=arcpy.Polyline(base)
    irec.shape=line
    irec.z=z
    irec.minimum=minimum
    irecs.insertRow(irec)
    del base            

    #next rec
    n+=1
    rec=recs.next()
        

#cleanUp
del irec
del irecs
del rec
del recs


##print arcpy.GetCount_management("Ridgelines")

#cleanup
print("cleanUp")
arcpy.Delete_management("buildings1")
arcpy.Delete_management("ridgelines1")
arcpy.Delete_management("ridgelines2")



print("completed")
