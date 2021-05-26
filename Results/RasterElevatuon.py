import arcpy
arcpy.env.overwriteOutput = True
sitesFc = arcpy.GetParameterAsText(0)
elevRas = arcpy.GetParameterAsText(1)
resultWorkspace = arcpy.GetParameterAsText(2)
arcpy.env.workspace = resultWorkspace

resFc = "rec_sites.shp"
arcpy.CopyFeatures_management(sitesFc, resFc)

if arcpy.Describe(resFc).spatialReference.name == arcpy.Describe(elevRas).spatialReference.name:
    arcpy.AddMessage('Coordinate systems are identical')
else:
    rasterProj = arcpy.Describe(elevRas).spatialReference.name
    arcpy.AddMessage('Coordinate systems differ. Projecting the feature class to {}'.format(rasterProj))
    arcpy.Project_management(resFc, resFc, rasterProj)

res_xy = []
res_elev = []
with arcpy.da.SearchCursor(resFc, ("SHAPE@XY",)) as cursor:
    for row in cursor:
        res_xy.append(row[0])  #[[x, y], [x1, y1]]
for xy in res_xy:
    result = arcpy.GetCellValue_management(elevRas, str(xy[0]) + " " + str(xy[1]))
    res_elev.append(result.getOutput(0))
arcpy.AddMessage("Extracted cell values from DEM")


arcpy.AddField_management(resFc, "HEIGHT", "SHORT")
with arcpy.da.UpdateCursor(resFc, ("HEIGHT",)) as cursor:
    i = 0
    for row in cursor:
        row[0] = res_elev[i]
        cursor.updateRow(row)
        i += 1
arcpy.AddMessage("Created HEIGHT field and populated with extracted values")
