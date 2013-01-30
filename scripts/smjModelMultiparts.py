#smjModelMultiparts.py

#purpse:
#model Building Footprints Based on Change in Height Observation from Lidar

#Owners
#Susan Jones & Amit Kokje
#Spatial Logic Limited
#Auckland, New Zealand

#sjones@spatiallogic.co.nz
#http://www.spatiallogic.co.nz/

#30 January 2013

#import Modules
import arcpy, string, fpformat

#banner
print("***\nMODEL MULTIPART BUILDINGS\n***")

#datasets
#TODO: Place the Data Sources Here
print("***get Datasets")
gdb=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb"
buildingFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\BuildingFootprints"
lidarFc=r"D:\Temp\Cera_Lidar\CBC_Modelling\CBD_Buildings.gdb\Lidar"

#set Environment
arcpy.env.workspace=gdb
arcpy.env.overwriteOutput=1
arcpy.env.outputZFlag="Enabled"

#create Featureclass
descfc=arcpy.Describe(buildingFc)
arcpy.CreateFeatureclass_management (gdb, "Structures", "POLYGON", lidarFc, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE", descfc.spatialReference)
arcpy.AddField_management(gdb+"\\Structures","MINIMUM","LONG")

#make Search Cursor for Buildings
arcpy.MakeFeatureLayer_management(buildingFc,"buildings")
arcpy.MakeFeatureLayer_management(lidarFc,"lidar1")
n=0
recs=arcpy.SearchCursor("buildings")
rec=recs.next()
while rec:

    #make extent
    sql="\"OBJECTID\"="+str(rec.objectid)
    arcpy.MakeFeatureLayer_management("buildings","building",sql)

    #clip
    arcpy.Clip_analysis("lidar1","building","surfacePts")
    print arcpy.GetCount_management("surfacePts")

    #update Z
    minimum=9999
    srecs=arcpy.UpdateCursor("surfacePts")
    srec=srecs.next()
    while srec:
        srec.z=round(srec.z,0)
        if srec.Z < minimum:
            minimum=srec.Z
        srecs.updateRow(srec)
        #next srec
        srec=srecs.next()
    del srec
    del srecs

    #extent
    print "minimum:"+str(minimum)
    sfc=arcpy.Describe("building")
    arcpy.env.extent=sfc.extent

    #minimum Bounding Geometry
    arcpy.MinimumBoundingGeometry_management("surfacePts", "minimumBounding", "RECTANGLE_BY_WIDTH", "LIST", "Z")
    arcpy.AddField_management(gdb+"\\minimumBounding","MINIMUM","LONG")

##    print arcpy.GetCount_management("minimumBounding")

    #geometry
    try:
        urecs=arcpy.UpdateCursor("minimumBounding")
        urec=urecs.next()
        while urec:
            if urec.Z>minimum:
                urec.minimum=minimum
            else:
                urec.minimum=0
            urecs.updateRow(urec)
##            print "updated"
            #next urec
            urec=urecs.next()
        del urec
        del urecs
    except:
        print "next"

    #append
##    print "append"
    arcpy.Clip_analysis("minimumBounding","building","minimumBounding1")
    arcpy.Append_management("minimumBounding1","Structures","NO_TEST")

    #extent
    sfc=arcpy.Describe("buildings")
    arcpy.env.extent=sfc.extent

    #next rec
    n+=1
    rec=recs.next()
        

#cleanUp
del rec
del recs

#reset
arcpy.Delete_management("minimumBounding")
arcpy.Delete_management("minimumBounding1")
arcpy.Delete_management("building")
arcpy.Delete_management("buildings")
arcpy.Delete_management("lidar1")

print arcpy.GetCount_management("Structures")

print("completed")