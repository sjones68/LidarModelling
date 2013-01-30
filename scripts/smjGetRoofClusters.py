#smjGetRoofClusters.py

#import Modules
import arcpy, string, datetime, fpformat, operator, os

#banner
startTime=datetime.datetime.now()
print("***\nMODEL BUILDING CLUSTERS\n***")

#get Parameters - lidar Data, building Footprints, output Geodatabase
print("***get Parameters")
##fc=arcpy.GetParameterAsText(0)
##buildings=arcpy.GetParameterAsText(1)
##folder=arcpy.GetParameterAsText(2)
fc=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\Residential_roofs.gdb\LiDAR_BuildingOnly"
buildings=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\Residential_roofs.gdb\Buildings"
folder=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\outGdb.gdb"

#set Environment
arcpy.env.workspace=folder
arcpy.env.overwriteOutput=1

#make Ridgelines
print("***make Featureclasses")
sr=arcpy.SpatialReference()
sr.factoryCode=2193
arcpy.CreateFeatureclass_management(folder,"BuildingClusters","polygon","","disabled","enabled",sr)
irecs=arcpy.InsertCursor("BuildingClusters")

#get Unique Buildings
print("***get Unique Buildings")
cnt=0
bfpLst=[]
arcpy.MakeFeatureLayer_management(fc,"fc1")

arcpy.MakeFeatureLayer_management(buildings,"buildings")
recs=arcpy.SearchCursor("buildings")
rec=recs.next()
#cycle Buildings
while rec and cnt<3:

    try:
        #TODO: make sql
        sql="\"OBJECTID\" = "+str(rec.objectid)
        print(sql)
        arcpy.MakeFeatureLayer_management(buildings,"buildings1",sql)

        #TODO: set Mask
        arcpy.env.mask="buildings1"

        #TODO: get Lidar Observations
        arcpy.Clip_analysis("fc1","buildings1","fc2")

        #TODO: run Cluster Analysis
        dt=datetime.datetime.now()
        arcpy.ClustersOutliers_stats("fc2","Z","fc3","ZONE_OF_INDIFFERENCE","EUCLIDEAN_DISTANCE")
        arcpy.MinimumBoundingGeometry_management("fc3","fc4","CONVEX_HULL","LIST","COTYPE")
        nrecs=arcpy.SearchCursor("fc4")
        nrec=nrecs.next()
        while nrec:
            irec=irecs.newRow()
            irec.shape=nrec.shape
            irecs.insertRow(irec)
            #next nrec
            nrec=nrecs.next()
        print("Elapsed:"+str(cnt)+"\t"+str(datetime.datetime.now()-dt))

    except:
        print "cannot Process"

    #increment Count Per Building
    cnt+=1
    if operator.mod(cnt,100)==0:
        print(str(cnt)+":processed")

    #next rec
    rec=recs.next()

#clip
del irecs
arcpy.Union_analysis([["BuildingClusters",1],[buildings,1]],"BuildingClusters1")
arcpy.Clip_analysis("BuildingClusters1",buildings,"BuildingClusters2")

#completed
print("completed")
print("Time To Complete:\t"+str(datetime.datetime.now()-startTime))
