#smjGetRoofHeights.py

#import Modules
import arcpy, string, datetime, fpformat, operator, os

#slopeCalculation
def slopeCalculation(pt1,pt2):
    dx2=operator.pow(operator.abs(operator.sub(pt1.X,pt2.X)),2)
    dy2=operator.pow(operator.abs(operator.sub(pt1.Y,pt2.Y)),2)
    dz2=operator.pow(operator.abs(operator.sub(pt1.Z,pt2.Z)),2)
    if dz2>0:
        vertical=operator.pow(dz2,0.5)
        horiz=operator.pow(dx2+dy2,0.5)
        slope=(vertical/horiz)*100
    else:
        slope=999
    return slope

#get Distance
def calcDistance(ptA,ptB):
    distSq=operator.pow(operator.sub(ptA.X,ptB.X),2) + operator.pow(operator.sub(ptA.Y,ptB.Y),2)
    distance=operator.pow(distSq,0.5)
    return distance

#define Ridge
def defineRidge(minshp,maxshp,sr):
    
    #TODO: for each point in the Ridge
    for minpt in minshp:
        distance=20
        for maxpt in maxshp:
            #TODO: Compare Distance
           testDistance=calcDistance(minpt,maxpt)
           if testDistance<distance:
               linepts=arcpy.Array()
               linepts.add(minpt)
               linepts.add(maxpt)
               sl=slopeCalculation(minpt,maxpt)
               newLine=arcpy.Polyline(linepts,sr)
               distance=testDistance
        
        #TODO: add with Base of Roof
        try:
            nrec=nrecs.newRow()
            nrec.shape=newLine
            nrecs.insertRow(nrec)
        except:
            status="continue"
            
    #TODO: add Top Continue
    try:
        pt=maxshp[0]
        m=1
        while m<len(maxshp):
            linepts=arcpy.Array()
            linepts.add(pt)
            linepts.add(maxshp[m])
            newLine=arcpy.Polyline(linepts,sr)
            if newLine.length>0:
                nrec=nrecs.newRow()
                nrec.shape=newLine
                nrecs.insertRow(nrec)
            m+=1
    except:
        status="continue"
    
    #TODO: add The Base
    try:
        nrec=nrecs.newRow()
        newLine=arcpy.Polyline(minshp,sr)
        nrec.shape=newLine
        nrecs.insertRow(nrec)
    except:
        status="continue"

    
#define Building
def defineBuilding(minshp,sr):

    #TODO: get Z
    for mn in minshp:
        z=mn.Z
        mn.Z=0
    
    #TODO: for each point in the Ridge
    newPolygon=arcpy.Polygon(minshp,sr)
    
    #TODO: add The Base
    brec=brecs.newRow()
    brec.shape=newPolygon
    #get z
    brec.Z=z
    brecs.insertRow(brec)
    

#banner
print("\nMODEL BUILDING HEIGHTS")

#get Parameters - x, y, z, bfp_area
print("***get Parameters")
fc=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\Residential_roofs.gdb\Buildings"
buildings=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\Residential_roofs.gdb\BuildingClusters1"
folder=r"C:\Contracts\Explorer Graphics\CERA\lidar3D\outGdb.gdb"

#set Environment
arcpy.env.workspace=folder
arcpy.env.overwriteOutput=1

#make Ridgelines
print("***make Featureclasses")
sr=arcpy.SpatialReference()
sr.factoryCode=2193
arcpy.CreateFeatureclass_management(folder,"Ridgelines","polyline","","disabled","enabled",sr)
arcpy.CreateFeatureclass_management(folder,"Buildings2","polygon","","disabled","enabled",sr)
arcpy.AddField_management(folder+"\\Buildings2","Z","DOUBLE")

#get Unique Buildings
print("***get Unique Buildings")
cnt=0
bfpLst=[]
nrecs=arcpy.InsertCursor("Ridgelines")
arcpy.MakeFeatureLayer_management(fc,"fc1")
brecs=arcpy.InsertCursor(folder+"\\Buildings2")

arcpy.MakeFeatureLayer_management(buildings,"buildings")
recs=arcpy.SearchCursor("buildings")
rec=recs.next()
#cycle Buildings
while rec:

    try:
        #TODO: make sql
        sql="\"OBJECTID\" = "+str(rec.objectid)
        arcpy.MakeFeatureLayer_management(buildings,"buildings1",sql)

        #TODO: set Mask
        arcpy.env.mask="buildings1"

        #TODO: get Lidar Observations
        arcpy.SelectLayerByLocation_management("fc1","COMPLETELY_WITHIN","buildings1")
        arcpy.CopyFeatures_management("fc1","fc2")

        #TODO: get Minimum and Maximum
        irecs=arcpy.SearchCursor("fc2")
        irec=irecs.next()
        minValue=string.atof(fpformat.fix(irec.Z,0))
        maxValue=string.atof(fpformat.fix(irec.Z,0))
        pts=1
        while irec:
            #TODO: test MINIMUM HEIGHT
            if irec.Z<minValue:
                minValue=string.atof(fpformat.fix(irec.Z,0))
            #TODO: test MAXIMUM HEIGHT
            if string.atof(fpformat.fix(irec.Z,0))>maxValue:
                maxValue=string.atof(fpformat.fix(irec.Z,0))
                pts==0
            elif string.atof(fpformat.fix(irec.Z,0))==maxValue:
                pts+=1
            else:
                pts+=0
            irec=irecs.next()

        #TODO: get Lower Roof
        minshp=arcpy.Array()
        shp=rec.shape.getPart(0)
        for pt in shp:
            pt.Z=minValue
            minshp.add(pt)
            
        #TODO: get Top Ridge
        maxshp=arcpy.Array()
        irecs=arcpy.SearchCursor("fc2")
        irec=irecs.next()
        while irec:
            #check
            if string.atof(fpformat.fix(irec.Z,0))==maxValue:
                pt=irec.shape.getPart(0)
                pt.Z=maxValue
                maxshp.add(pt)
            irec=irecs.next()

        #TODO: defineRidge
        testpt=maxshp[0]

        #initialise Extents
        n=0
        while n<=len(maxshp)-1:
            pt=maxshp[n]
            #pt3
            if pt.Y>=testpt.Y:
                pt3=pt
            else:
                pt3=testpt
            #pt1
            if pt.Y<=testpt.Y:
                pt1=pt
            else:
                pt1=testpt
            #pt4
            if pt.X>=testpt.X:
                pt4=pt
            else:
                pt4=testpt
            #pt2
            if pt.X<=testpt.X:
                pt2=pt
            else:
                pt2=testpt
            #next pt
            testpt=pt
            n+=1

        #print Extents
        maxshp=[]
        maxshp.append(pt1)
        maxshp.append(pt2)
        maxshp.append(pt3)
        maxshp.append(pt4)
        defineRidge(minshp,maxshp,sr)
            
        #TODO: defineBuilding
        defineBuilding(minshp,sr)

    except:
        print "cannot Process"

    #increment Count Per Building
    cnt+=1
    if operator.mod(cnt,10)==0:
        print str(cnt)+":processed"

    #next rec
    rec=recs.next()

#completed
del irec
del irecs
del rec
del recs
del nrecs
del brecs

#TODO: features To Polygons
print("***feature To Polygon")
if arcpy.Exists("Features3D"):
    arcpy.Delete_management("Features3D")
arcpy.FeatureToPolygon_management ("Ridgelines","Features3D")

#TODO: clip To Buildings
print("***clip To Building")
if arcpy.Exists("Rooves"):
    arcpy.Delete_management("Rooves")
arcpy.Clip_analysis("Features3D","buildings","Rooves")


#TODO: add Z
print("***add Z")
arcpy.AddField_management(folder+"\\Rooves","Z","DOUBLE")
arcpy.MakeFeatureLayer_management(folder+"\\Rooves","Rooves1")
nrecs=arcpy.UpdateCursor("Rooves1")
nrec=nrecs.next()
while nrec:
    shp=nrec.shape.getPart(0)
    htLst=[]
    for pt in shp:
        try:
            htLst.append(pt.Z)
        except:
            status="continue"
    htLst.sort()
    #TODO: update Z
    try:
        if htLst[0]==0:
            status="do Somethig with triagulated polygon"
        else:
            nrec.Z=htLst[len(htLst)-1]
            nrecs.updateRow(nrec)
    except:
        status="continue"
    nrec=nrecs.next()

#TODO: feature To 3D
if arcpy.Exists("Buildsing3D"):
    arcpy.Delete_management("Buildings3D")
arcpy.Copy_management("Buildings2","Buildings3D")
arcpy.Delete_management("Buildings2")

#completed
del nrecs
print("completed")
