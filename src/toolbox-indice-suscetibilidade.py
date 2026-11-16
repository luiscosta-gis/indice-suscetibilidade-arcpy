# -*- coding: utf-8 -*-
"""
Versão Parametrizada para Integração em ArcToolbox (.tbx)
Nota: Script experimental desenvolvido para receber parâmetros dinâmicos da interface do ArcGIS.
"""

import os
import arcpy
from arcpy import env
from arcpy.sa import *

arcpy.CheckOutExtension("3D")
arcpy.CheckOutExtension("Spatial")
arcpy.env.cellSize = 5
arcpy.env.overwriteOutput = True

# Parâmetros recebidos da interface da ArcToolbox
input_folder = arcpy.GetParameterAsText(0)   # Pasta com os dados de entrada
out_system = arcpy.GetParameterAsText(1)     # Sistema de coordenadas de destino
out_workspace = arcpy.GetParameterAsText(2)  # Pasta de saída dos resultados
out_indice1 = arcpy.GetParameterAsText(3)    # Caminho de saída para o Índice 1
out_indice2 = arcpy.GetParameterAsText(4)    # Caminho de saída para o Índice 2

arcpy.env.workspace = input_folder
spatial_ref = arcpy.SpatialReference(3763) if not out_system else out_system

# Definir e projetar Feature Classes
fclist = arcpy.ListFeatureClasses()
for fc in fclist:
    arcpy.DefineProjection_management(fc, spatial_ref)
    dsc = arcpy.Describe(fc)
    if dsc.SpatialReference.Name != "Unknown":
        outfc = os.path.join(out_workspace, fc)
        arcpy.Project_management(fc, outfc, spatial_ref)

# Projetar MDE e calcular declives
in_mde = os.path.join(input_folder, "mde_5m")
out_mde = os.path.join(out_workspace, "mde_etrs.tif")
arcpy.ProjectRaster_management(in_mde, out_mde, spatial_ref)

out_declives = os.path.join(out_workspace, "declives.tif")
arcpy.Slope_3d(out_mde, out_declives, "PERCENT_RISE")

remap_declives = RemapValue([[0, 2, 100], [2, 6, 90], [6, 12, 50], [12, 18, 30], [18, 200, 10]])
declives_rec = Reclassify(out_declives, "VALUE", remap_declives, "NODATA")
declives_rec_path = os.path.join(out_workspace, "Declives_Rec")
declives_rec.save(declives_rec_path)

# Converter Geologia (D, R, A) e Uso do Solo (LU) para Raster
in_geologia = os.path.join(out_workspace, "inter_filoes_geol.shp")
out_rasterD = os.path.join(out_workspace, "Parametro_D")
out_rasterR = os.path.join(out_workspace, "Parametro_R")
out_rasterA = os.path.join(out_workspace, "Parametro_A")

arcpy.FeatureToRaster_conversion(in_geologia, "D", out_rasterD, 5)
arcpy.FeatureToRaster_conversion(in_geologia, "R", out_rasterR, 5)
arcpy.FeatureToRaster_conversion(in_geologia, "A", out_rasterA, 5)

in_uso_solo = os.path.join(out_workspace, "uso_solo.shp")
out_rasterLU = os.path.join(out_workspace, "Parametro_LU")
arcpy.PolygonToRaster_conversion(in_uso_solo, "lu", out_rasterLU, "", "", 5)

# Cálculo dos Índices de Suscetibilidade
indice1 = (Raster(out_rasterD) * 0.24) + (Raster(out_rasterA) * 0.27) + (Raster(out_rasterR) * 0.33) + (Raster(declives_rec_path) * 0.16)
indice1.save(out_indice1 if out_indice1 else os.path.join(out_workspace, "Indice1"))

indice2 = (Raster(out_rasterD) * 0.186) + (Raster(out_rasterA) * 0.259) + (Raster(out_rasterR) * 0.212) + (Raster(declives_rec_path) * 0.121) + (Raster(out_rasterLU) * 0.222)
indice2.save(out_indice2 if out_indice2 else os.path.join(out_workspace, "Indice2"))

arcpy.AddMessage("Processamento concluido com sucesso.")