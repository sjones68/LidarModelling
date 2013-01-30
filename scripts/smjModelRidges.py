#smjModelRidges.py

#purpse:
#model Model Roof Ridges using Change of Height

#Owners
#Susan Jones & Amit Kokje
#Spatial Logic Limited
#Auckland, New Zealand

#sjones@spatiallogic.co.nz
#http://www.spatiallogic.co.nz/

#30 January 2013

#import Modules
import arcpy, string, fpformat

#makeLine
def makeLine(pt1,pt2,pt3,pt4):

    x1=(pt1.X+pt2.X)/2
    y1=(pt1.Y+pt2.Y)/2

    x2=(pt3.X+pt4.X)/2
    y2=(pt3.Y+pt4.Y)/2

    ptA=arcpy.Point(x1,y1)
    ptB=arcpy.Point(x2,y2)

    lineArray=arcpy.Array([ptA, ptB])
    
    line=arcpy.Polyline(lineArray)
    return line


#banner
print("***\nMODEL MULTIPART BUILDINGS\n***")

#datasets
#TODO: Place the Data Sources Here
print("***get Datasets")
gdb=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb"
buildingFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\BuildingFootprints"
structuresFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\Structures"

#set Environment
arcpy.env.workspace=gdb
arcpy.env.overwriteOutput=1
arcpy.env.outputZFlag="Enabled"

#create Featureclass
descfc=arcpy.Describe(structuresFc)
arcpy.CreateFeatureclass_management (gdb, "Ridgelines", "POLYLINE", structuresFc, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", descfc.spatialReference)


#insert Recs
print("insert Records")
irecs=arcpy.InsertCursor(gdb+"\\Ridgelines")

#make Search Cursor for Buildings
arcpy.MakeFeatureLayer_management(buildingFc,"buildings1")
n=0
recs=arcpy.SearchCursor("buildings1")
print arcpy.GetCount_management("buildings1")
rec=recs.next()
while rec:

    #make extent
    sql="\"OBJECTID\"="+str(rec.objectid)
    arcpy.MakeFeatureLayer_management(buildingFc, "building", sql)
    arcpy.MakeFeatureLayer_management(structuresFc,"struct1")
    arcpy.SelectLayerByLocation_management("struct1", "INTERSECT", "building")
##    print "noFeatures:"+str(arcpy.GetCount_management("struct1"))

    #get Ridge
    tHgt=0
    srecs=arcpy.SearchCursor("struct1")
    srec=srecs.next()
    while srec:

        #compare
        if srec.Z>tHgt:
            testArray=srec.shape.getPart(0)
            tHgt=srec.Z
            minimum=srec.minimum

        #next srec   
        srec=srecs.next()
        
    #delete
    del srec
    del srecs

    #get Roofs Stuff
    if len(testArray)==5:
        print "hgt:"+str(tHgt)
        print "min:"+str(minimum)

        #make Line A
        pt1=testArray[0]
        pt2=testArray[1]
        pt3=testArray[2]
        pt4=testArray[3]
        lineA=makeLine(pt1,pt2,pt3,pt4)
        print "lineA:"+str(lineA.length)

        #make Line B
        pt1=testArray[1]
        pt2=testArray[2]
        pt3=testArray[3]
        pt4=testArray[4]
        lineB=makeLine(pt1,pt2,pt3,pt4)
        print "lineB:"+str(lineB.length)        

        #compare Lines And Populate Record
        irec=irecs.newRow()
        if lineB.length>lineA.length:
            irec.shape=lineB
        else:
            irec.shape=lineA
        irec.Z=tHgt
        irec.minimum=minimum
        irecs.insertRow(irec)

        #del irec
        del irec

    #next rec
    n+=1
    rec=recs.next()
        

#cleanUp
del irecs
del rec
del recs


##print arcpy.GetCount_management("Ridgelines")

#cleanup
print("cleanUp")
arcpy.Delete_management("building")
arcpy.Delete_management("buildings1")
arcpy.Delete_management("struct1")

print("completed")
