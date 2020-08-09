import arcpy

#pokus pro zpracovani vrstevnic po jedny!! vychazi z c_gen.py
#nastaven workspace na slozku, dale je potreba, aby ve slozce byl podslozka output s databazi db.gdb


def three_points(contour, p_contour_low, p_contour_high):
    near_table_low = "near_table_low"
    near_table_high = "near_table_high"
    closest_count = 1
    f_con = "FINAL_vrstevnice"
    fc = "linie_spojnice"
    return_feature = "returned"
    arcpy.CreateFeatureclass_management("/output/db.gdb", f_con, "POLYLINE", "", "", "", 5514)
    arcpy.AddField_management("/output/db.gdb/" + f_con, "Contour", "SHORT")
    with arcpy.da.SearchCursor(contour, ["OID@", "SHAPE@", "Contour"]) as row:  # prochazi vsechny vrstevnice
        i = 1
        for line in row:
            array_c = arcpy.Array()
            if not line[1]: # kontrola prazdneho atributu, musim poresit, co se tady deje
                print ("preskoceno line")
                continue

            p_contour = arcpy.FeatureVerticesToPoints_management(line[1], "/output/db.gdb/p_contour","ALL")  # jednu vrstevnici prevede na body
            with arcpy.da.SearchCursor(p_contour, ["OID@", "SHAPE@", "SHAPE@X", "SHAPE@Y"]) as c_row:  # cursor bodu ve vrstevnici
                for point in c_row:
                    array = arcpy.Array()
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_low, near_table_low, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL",
                                                     closest_count)  # nejblizsi body u vyskoveho bufferu
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_high, near_table_high, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL", closest_count)
                    with arcpy.da.SearchCursor(near_table_low,
                                               ['NEAR_X', 'NEAR_Y']) as n_low_row:  # najde nejblizsi body
                        for p in n_low_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_low_row
                    with arcpy.da.SearchCursor(near_table_high, ['NEAR_X', 'NEAR_Y']) as n_high_row:
                        for p in n_high_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_high_row
                    existed_p = arcpy.Point(point[2], point[3])
                    array.append(existed_p)
                    out_feature_class = "centroid_polygonu"
                    polygon = arcpy.Polygon(array)
                    arcpy.FeatureToPoint_management(polygon, "/output/db.gdb/" + out_feature_class, "CENTROID")
                    with arcpy.da.SearchCursor("/output/db.gdb/" + out_feature_class,
                                               ["OID@", "SHAPE@X", "SHAPE@Y"]) as c_point:
                        for p in c_point:
                            p1 = arcpy.Point(p[1], p[2])
                            array_c.append(p1)
                    del c_point

            del c_row
            if not array_c: #kontrola prazdneho listu, nebo co se deje tady
                print ("preskoceno prazdne array_c")
                continue
            linie_final = arcpy.Polyline(array_c)
            arcpy.FeatureClassToFeatureClass_conversion(linie_final, "/output/db.gdb", fc)
            arcpy.AddField_management("/output/db.gdb/" + fc, "Contour", "SHORT")
            with arcpy.da.UpdateCursor("/output/db.gdb/" + fc, "Contour") as row_for_one:
                for value in row_for_one:
                    value[0] = row[2]
                    row_for_one.updateRow(value)
            del row_for_one
            del value

            with arcpy.da.SearchCursor("/output/db.gdb/" + fc, ["SHAPE@", "Contour"]) as row_for_one:
                for geom in row_for_one:
                    cursor = arcpy.da.InsertCursor("/output/db.gdb/" + f_con, ["SHAPE@", "Contour"])
                    cursor.insertRow((geom[0], geom[1]))

            del cursor
            del row_for_one
            print(i)
            i = i + 1

    arcpy.CopyFeatures_management("/output/db.gdb/" + f_con, "/output/db.gdb/" + return_feature)
    del row
    return return_feature


def one_nearest(contour, p_contour_low, p_contour_high):
    near_table_low = "near_table_low"
    near_table_high = "near_table_high"
    closest_count = 1
    f_con = "FINAL_vrstevnice"
    fc = "linie_spojnice"
    return_feature = "returned"
    arcpy.CreateFeatureclass_management("/output/db.gdb", f_con, "POLYLINE", "", "", "", 5514)
    arcpy.AddField_management("/output/db.gdb/" + f_con, "Contour", "SHORT")
    with arcpy.da.SearchCursor(contour, ["OID@", "SHAPE@", "Contour"]) as row:  # prochazi vsechny vrstevnice
        i = 1
        for line in row:
            array_c = arcpy.Array()
            if not line[1]: # kontrola prazdneho atributu
                print ("preskoceno line")
                continue
            p_contour = arcpy.FeatureVerticesToPoints_management(line[1], "/output/db.gdb/p_contour","ALL")  # jednu vrstevnici prevede na body
            with arcpy.da.SearchCursor(p_contour, ["OID@", "SHAPE@"]) as c_row:  # cursor bodu ve vrstevnici
                for point in c_row:
                    array = arcpy.Array()
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_low, near_table_low, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL",
                                                     closest_count)  # nejblizsi body u vyskoveho bufferu
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_high, near_table_high, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL", closest_count)
                    with arcpy.da.SearchCursor(near_table_low,
                                               ['NEAR_X', 'NEAR_Y']) as n_low_row:  # najde nejblizsi body
                        for p in n_low_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_low_row
                    with arcpy.da.SearchCursor(near_table_high, ['NEAR_X', 'NEAR_Y']) as n_high_row:
                        for p in n_high_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_high_row

                    linie = arcpy.Polyline(array)
                    centroid = linie.centroid
                    array_c.append(centroid)
            del c_row
            if not array_c: #kontrola prazdneho listu
                print ("preskoceno prazdne array_c")
                continue
            linie_final = arcpy.Polyline(array_c)
            arcpy.FeatureClassToFeatureClass_conversion(linie_final, "/output/db.gdb", fc)
            arcpy.AddField_management("/output/db.gdb/" + fc, "Contour", "SHORT")
            with arcpy.da.UpdateCursor("/output/db.gdb/" + fc, "Contour") as row_for_one:
                for value in row_for_one:
                    value[0] = row[2]
                    row_for_one.updateRow(value)
            del row_for_one
            del value

            with arcpy.da.SearchCursor("/output/db.gdb/" + fc, ["SHAPE@", "Contour"]) as row_for_one:
                for geom in row_for_one:
                    cursor = arcpy.da.InsertCursor("/output/db.gdb/" + f_con, ["SHAPE@", "Contour"])
                    cursor.insertRow((geom[0], geom[1]))

            del cursor
            del row_for_one
            print(i)
            i = i + 1

    arcpy.CopyFeatures_management("/output/db.gdb/" + f_con, "/output/db.gdb/" + return_feature)
    del row
    return return_feature


#pro vice bodu


def more_nearest(contour, p_contour_low, p_contour_high, count):
    near_table_low = "near_table_low"
    near_table_high = "near_table_high"
    closest_count = count
    f_con = "FINAL_vrstevnice"
    fc = "linie_spojnice"
    return_feature = "returned"
    arcpy.CreateFeatureclass_management("/output/db.gdb", f_con, "POLYLINE", "", "", "", 5514)
    arcpy.AddField_management("/output/db.gdb/" + f_con, "Contour", "SHORT")
    with arcpy.da.SearchCursor(contour, ["OID@", "SHAPE@", "Contour"]) as row:  # prochazi vsechny vrstevnice
        i = 1
        for line in row:
            array_c = arcpy.Array()
            if not line[1]: # kontrola prazdneho atributu
                print ("preskoceno line")
                continue

            p_contour = arcpy.FeatureVerticesToPoints_management(line[1], "/output/db.gdb/p_contour","ALL")  # jednu vrstevnici prevede na body
            with arcpy.da.SearchCursor(p_contour, ["OID@", "SHAPE@"]) as c_row:  # cursor bodu ve vrstevnici
                for point in c_row:
                    array = arcpy.Array()
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_low, near_table_low, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL",
                                                     closest_count)  # nejblizsi body u vyskoveho bufferu
                    arcpy.GenerateNearTable_analysis(point[1], p_contour_high, near_table_high, "#", "LOCATION",
                                                     "NO_ANGLE", "ALL", closest_count)
                    with arcpy.da.SearchCursor(near_table_low,
                                               ['NEAR_X', 'NEAR_Y']) as n_low_row:  # najde nejblizsi body
                        for p in n_low_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_low_row
                    with arcpy.da.SearchCursor(near_table_high, ['NEAR_X', 'NEAR_Y']) as n_high_row:
                        for p in n_high_row:
                            p1 = arcpy.Point(p[0], p[1])
                            array.append(p1)
                    del n_high_row

                    out_feature_class = "centroid_polygonu"
                    polygon = arcpy.Polygon(array)
                    arcpy.FeatureToPoint_management(polygon, "/output/db.gdb/" + out_feature_class, "CENTROID")
                    with arcpy.da.SearchCursor("/output/db.gdb/" + out_feature_class, ["OID@", "SHAPE@X", "SHAPE@Y"]) as c_point:
                        for p in c_point:
                            p1 = arcpy.Point(p[1], p[2])
                            array_c.append(p1)
                    del c_point

            del c_row
            if not array_c: #kontrola prazdneho listu
                print ("preskoceno prazdne array_c")
                continue
            linie_final = arcpy.Polyline(array_c)
            arcpy.FeatureClassToFeatureClass_conversion(linie_final, "/output/db.gdb", fc)
            arcpy.AddField_management("/output/db.gdb/" + fc, "Contour", "SHORT")
            with arcpy.da.UpdateCursor("/output/db.gdb/" + fc, "Contour") as row_for_one:
                for value in row_for_one:
                    value[0] = row[2]
                    row_for_one.updateRow(value)
            del row_for_one
            del value

            with arcpy.da.SearchCursor("/output/db.gdb/" + fc, ["SHAPE@", "Contour"]) as row_for_one:
                for geom in row_for_one:
                    cursor = arcpy.da.InsertCursor("/output/db.gdb/" + f_con, ["SHAPE@", "Contour"])
                    cursor.insertRow((geom[0], geom[1]))

            del cursor
            del row_for_one
            print(i)
            i = i + 1

    arcpy.CopyFeatures_management("/output/db.gdb/" + f_con, "/output/db.gdb/" + return_feature)
    del row
    return return_feature



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
contours = arcpy.SurfaceContour_3d(triangle, "contour.shp", 1)
print ("Contours created")

#vytvoreni hranicnich vrstevnic
contour_low = arcpy.SurfaceContour_3d(triangle, "/output/db.gdb/contour_low", 1, 0.1)
contour_high = arcpy.SurfaceContour_3d(triangle, "/output/db.gdb/contour_high", 1, -0.1)
point_contour_low = arcpy.FeatureVerticesToPoints_management(contour_low, "/output/db.gdb/p_contour_low", "ALL")
point_contour_high = arcpy.FeatureVerticesToPoints_management(contour_high, "/output/db.gdb/p_contour_high", "ALL")
# vymazani dat v pameti
del contour_high, contour_low, triangle

nneighbours = 5
if nneighbours > 1:
    vrstevnice = more_nearest(contours, point_contour_low, point_contour_high, nneighbours)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/prvni_iterace_polygon_5nn")
    print ("prvni iterace done")
    vrstevnice = more_nearest("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high, nneighbours)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/druha_iterace_polygon_5nn")
    print ("druha iterace done")
    vrstevnice = more_nearest("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high, nneighbours)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/treti_iterace_polygon_5nn")
    print ("treti iterace done")
elif nneighbours < 1:
    vrstevnice = one_nearest(contours, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/prvni_iterace")
    print ("prvni iterace done")
    vrstevnice = one_nearest("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/druha_iterace")
    print ("druha iterace done")
    vrstevnice = one_nearest("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/treti_iterace")
    print ("treti iterace done")
else:
    vrstevnice = three_points(contours, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/prvni_iterace_tri_body")
    print ("prvni iterace done")
    vrstevnice = three_points("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/druha_iterace_tri_body")
    print ("druha iterace done")
    vrstevnice = three_points("/output/db.gdb/" + vrstevnice, point_contour_low, point_contour_high)
    arcpy.CopyFeatures_management("/output/db.gdb/" + vrstevnice, "/output/db.gdb/treti_iterace_tri_body")
    print ("treti iterace done")










