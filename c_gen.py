import arcpy

#kontrola prepsani outputu a extensions
arcpy.env.overwriteOutput = 1
arcpy.env.workspace = "C:\Users\Marek\Documents\GitHub\contour-ArcMap-MeanMethod"
arcpy.CheckOutExtension("3D")

#vybrani zpracovavaneho pointcloudu
table = "C:\Users\Marek\Documents\GitHub\contour-ArcMap-MeanMethod\BILO48_5g_40k.csv"
out_Layer = "pointcloud"
x_coords = "X"
y_coords = "Y"
z_coords = "Z"

#vytvoreni bodoveho mracna do layer pro zpracovani
arcpy.MakeXYEventLayer_management(table, x_coords, y_coords, out_Layer, arcpy.SpatialReference(5514, 5705), z_coords)

print(arcpy.GetCount_management(out_Layer)) #kontrolni print poctu bodu

#ulozeni bodoveho mracna
saved_Layer = "out.lyr"
arcpy.SaveToLayerFile_management(out_Layer, saved_Layer)
print ("Point cloud created")

#vytvoreni TIN
triangle = arcpy.CreateTin_3d("TIN", arcpy.SpatialReference(5514, 5705), saved_Layer)
print ("TIN created")

#vytvoreni vrstevnic
contour = arcpy.SurfaceContour_3d(triangle, "contour.shp", 1)
print ("Contours created")

#vytvoreni hranicnich vrstevnic
contour_low = arcpy.SurfaceContour_3d(triangle, "contour_low.shp", 1, 0.1)
contour_high = arcpy.SurfaceContour_3d(triangle, "contour_high.shp", 1, -0.1)

#vytvoreni bodu na vrstevnici
#arcpy.GeneratePointsAlongLines_management("contour_low.shp", 'distance_intervals_low.shp', 'DISTANCE', Distance='100 meters')
#arcpy.GeneratePointsAlongLines_management("contour_high.shp", 'distance_intervals_high.shp', 'DISTANCE', Distance='100 meters')
#print ("PointsAlongLines created")

#vytvoreni bodu z vrstevnice
p_contour = arcpy.FeatureVerticesToPoints_management(contour, "p_contour.shp", "ALL")
p_contour_low = arcpy.FeatureVerticesToPoints_management(contour_low, "p_contour_low.shp", "ALL")
p_contour_high = arcpy.FeatureVerticesToPoints_management(contour_high, "p_contour_high.shp", "ALL")
print("Contours to Points")

#vytvoreni nearest_table
closest_count = 1 #kolik nejblizsich ma najit
near_table_low = "near_table_low"
near_table_high = "near_table_high"

arcpy.GenerateNearTable_analysis(p_contour, p_contour_low, near_table_low, "#", "LOCATION", "NO_ANGLE", "ALL", closest_count)
arcpy.GenerateNearTable_analysis(p_contour, p_contour_high, near_table_high, "#", "LOCATION", "NO_ANGLE", "ALL", closest_count)


#nalezeni nejblizsiho
#for p in p_contour:
#    arcpy.Near_analysis(p, p_contour_low,"10 Meters", "LOCATION")
#for p in p_contour:
#    arcpy.Near_analysis(p, p_contour_high,"10 Meters", "LOCATION")

#vytvoreni linii pokud hleda 1 nejblizsi

if closest_count == 1:
    fc = "linie.shp"
    arcpy.CreateFeatureclass_management("/output", fc, "POLYLINE", "", "", "", 5514)
    points = arcpy.GetCount_management(p_contour)
    points = int(points[0])
    while points != 0:
        expression = "NEAR_RANK <= {} AND IN_FID = {}".format(closest_count, points-1)
        with arcpy.da.SearchCursor(near_table_low, ['NEAR_X', 'NEAR_Y'], where_clause=expression) as cursor:
            for row in cursor:
                p1 = arcpy.Point(row[0], row[1])
        with arcpy.da.SearchCursor(near_table_high, ['NEAR_X', 'NEAR_Y'], where_clause=expression) as cursor:
            for row in cursor:
                p2 = arcpy.Point(row[0], row[1])
        array = arcpy.Array([p1, p2])
        linie = arcpy.Polyline(array)

        with arcpy.da.InsertCursor("/output/" + fc, "SHAPE@") as cursor:
            cursor.insertRow([linie])
        del cursor
        points = points - 1






