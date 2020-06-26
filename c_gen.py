import arcpy

#kontrola prepsani outputu a extensions
arcpy.env.overwriteOutput = 1
arcpy.env.workspace = "C:\Users\Marek\Documents\GitHub\contour-ArcMap"
arcpy.CheckOutExtension("3D")

#vybrani zpracovavaneho pointcloudu
table = "C:\Users\Marek\Documents\GitHub\contour-ArcMap\BILO48_5g_150k.csv"
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
arcpy.SurfaceContour_3d(triangle, "contour.shp", 1)
print ("Contours created")

#vytvoreni hranicnich vrstevnic
arcpy.SurfaceContour_3d(triangle, "contour_low.shp", 1, 0.1)
arcpy.SurfaceContour_3d(triangle, "contour_high.shp", 1, -0.1)

#vytvoreni bodu na vrstevnici
arcpy.GeneratePointsAlongLines_management("contour_low.shp", 'distance_intervals_low.shp', 'DISTANCE', Distance='100 meters')
arcpy.GeneratePointsAlongLines_management("contour_high.shp", 'distance_intervals_high.shp', 'DISTANCE', Distance='100 meters')
print ("PointsAlongLines created")
