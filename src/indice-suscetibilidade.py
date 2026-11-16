# -*- coding: utf-8 -*-
"""
Cálculo Automatizado do Índice de Suscetibilidade (com e sem Uso do Solo)
Autores: Luís Costa e Diogo Nogueira
Contexto: Mestrado em SIG e Ordenamento do Território (FLUP)
"""

import os
import arcpy
from arcpy import env
from arcpy.sa import *

# Ativar extensões necessárias e configurar ambiente
arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")

arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

# Definir pastas de entrada e saída (ajustar conforme o diretório local)
input_folder = "./Dados"
out_workspace = "./Resultados"
arcpy.env.workspace = input_folder

# 1. Verificar e definir o sistema de coordenadas (ETRS_1989_Portugal_TM06)
spatial_ref = arcpy.SpatialReference(3763)

fclist = arcpy.ListFeatureClasses()
for fc in fclist:
    arcpy.DefineProjection_management(fc, spatial_ref)
print("Define Projection concluido.")

# 2. Projetar as shapefiles para ETRS89 / Portugal TM06
for fc in fclist:
    dsc = arcpy.Describe(fc)
    if dsc.SpatialReference.Name == "Unknown":
        print("Saltou esta shape " + fc + " porque nao tem sistema de coordenadas.")
    else:
        outfc = os.path.join(out_workspace, fc)
        arcpy.Project_management(fc, outfc, spatial_ref)
print("Projection das shapefiles concluido.")

# 3. Projetar o Modelo Digital de Elevação (MDE)
in_mde = os.path.join(input_folder, "mde_5m")
out_mde = os.path.join(out_workspace, "mde_etrs.tif")
arcpy.ProjectRaster_management(in_mde, out_mde, spatial_ref)
print("Project raster concluido.")

# 4. Calcular e reclassificar Declives (Parâmetro T)
out_declives = os.path.join(out_workspace, "declives.tif")
arcpy.Slope_3d(out_mde, out_declives, "PERCENT_RISE")

remap_declives = RemapValue([[0, 2, 100], [2, 6, 90], [6, 12, 50], [12, 18, 30], [18, 200, 10]])
declives_rec = Reclassify(out_declives, "VALUE", remap_declives, "NODATA")
declives_rec_path = os.path.join(out_workspace, "Declives_Rec")
declives_rec.save(declives_rec_path)
print("Declives criados e reclassificados (Parametro T).")

# 5. Converter atributos geológicos para raster (Parâmetros D, R e A)
in_geologia = os.path.join(out_workspace, "inter_filoes_geol.shp")
out_rasterD = os.path.join(out_workspace, "Parametro_D")
out_rasterR = os.path.join(out_workspace, "Parametro_R")
out_rasterA = os.path.join(out_workspace, "Parametro_A")
cell_size = 5

arcpy.FeatureToRaster_conversion(in_geologia, "D", out_rasterD, cell_size)
arcpy.FeatureToRaster_conversion(in_geologia, "R", out_rasterR, cell_size)
arcpy.FeatureToRaster_conversion(in_geologia, "A", out_rasterA, cell_size)
print("Convertida shape da geologia para rasters dos Parametros D, R e A.")

# 6. Converter Uso do Solo para raster (Parâmetro LU)
in_uso_solo = os.path.join(out_workspace, "uso_solo.shp")
out_rasterLU = os.path.join(out_workspace, "Parametro_LU")
arcpy.PolygonToRaster_conversion(in_uso_solo, "lu", out_rasterLU, "", "", cell_size)
print("Convertida shape do uso do solo para raster Parametro_LU.")

# 7. Álgebra de Mapas: Índice de Suscetibilidade 1 (Sem Uso do Solo - Veríssimo, 2010)
pesoD, pesoR, pesoA, pesoT = 0.24, 0.33, 0.27, 0.16

indice1 = (Raster(out_rasterD) * pesoD) + (Raster(out_rasterA) * pesoA) + (Raster(out_rasterR) * pesoR) + (Raster(declives_rec_path) * pesoT)
indice1_path = os.path.join(out_workspace, "Indice1")
indice1.save(indice1_path)

remap_classes = RemapValue([[0, 30, 1], [30, 40, 2], [40, 50, 3], [50, 60, 4], [60, 70, 5], [70, 80, 6], [80, 90, 7], [90, 100, 8]])
rec_indice1 = Reclassify(indice1_path, "VALUE", remap_classes, "NODATA")
rec_indice1.save(os.path.join(out_workspace, "Rec_Indice1"))
print("Indice 1 (sem uso do solo) calculado e reclassificado.")

# 8. Álgebra de Mapas: Índice de Suscetibilidade 2 (Com Uso do Solo - Ribeiro, 2005b)
pesoD2, pesoR2, pesoA2, pesoT2, pesoLU = 0.186, 0.212, 0.259, 0.121, 0.222

indice2 = (Raster(out_rasterD) * pesoD2) + (Raster(out_rasterA) * pesoA2) + (Raster(out_rasterR) * pesoR2) + (Raster(declives_rec_path) * pesoT2) + (Raster(out_rasterLU) * pesoLU)
indice2_path = os.path.join(out_workspace, "Indice2")
indice2.save(indice2_path)

rec_indice2 = Reclassify(indice2_path, "VALUE", remap_classes, "NODATA")
rec_indice2.save(os.path.join(out_workspace, "Rec_Indice2"))
print("Indice 2 (com uso do solo) calculado e reclassificado.")