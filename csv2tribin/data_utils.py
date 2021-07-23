# -*- coding: utf-8 -*-
import os, struct, arcpy, glob
from .data_io import bin2gz

spatRef = arcpy.SpatialReference(4326)

def __get_lon_lat_height(line):
  component = line.split('\t')
  return (float(component[0]), float(component[1]), float(component[2]))

def __get_point_geometry(x = 1.0, y = 1.0, z = 1.0):
  point_shape = arcpy.Point()
  point_shape.X = x
  point_shape.Y = y
  point_shape.Z = z
  return arcpy.PointGeometry(point_shape)

def __create_point_feature(insert_cursor, shape, zvalue):
  ''' 私有方法。
  利用游标对象，插入一行记录。

  Args:
    insert_cursor: 游标
    shape: 几何
    zvalue: z值
  '''
  feature = insert_cursor.newRow()
  feature.shape = shape
  feature.zvalue = zvalue
  insert_cursor.insertRow(feature)

def parse_csv_to_pointshp(csvfiles, result_dir):
  ''' 转换csv文件到点文件

  Args:
    `csvfiles`: csv 文件列表，使用绝对路径。
  '''
  length = str(len(csvfiles))
  for index, csvfile in enumerate(csvfiles):
    print('CSV_2_PTSHP: Progress {}/{}, {}'.format(str(index + 1), length, csvfile))
    _, basename = os.path.split(csvfile)
    result_shp_filename = basename.replace('.txt', '.shp')

    feature_class = arcpy.CreateFeatureclass_management(result_dir, result_shp_filename, "POINT", "", "", "", spatRef)
    arcpy.AddField_management(feature_class, "zvalue", "DOUBLE")
    insert_cursor = arcpy.InsertCursor(feature_class)

    lines = open(csvfile).readlines()
    lines.pop(0) # 移除表头第一行
    for line in lines:
      x, y, z = __get_lon_lat_height(line)
      geom = __get_point_geometry(x, y, z)
      __create_point_feature(insert_cursor, geom, z)

def __point2tin(result_dir, shp_fullname, zvalue_name):
  '''使用点 shp 文件创建 tin 数据集

  Args:
    result_dir: tin 输出到哪里
    shp_fullname: 使用哪个 shp（绝对路径）
  '''
  params = shp_fullname + " zvalue Mass_Points <None>"
  shp_filename = os.path.basename(shp_fullname)
  arcpy.CreateTin_3d(out_tin = os.path.join(result_dir, shp_filename.replace('.shp', '')),
                     spatial_reference = "",
                     in_features = params)

def pointshp_to_tin(shp_files, result_dir):
  ''' 点 shp 转不规则三角网

  Args:
    shp_files: shp文件路径数组，要绝对路径
    result_dir: 输出 tin 数据集到何处
  '''
  length = str(len(shp_files))
  for index, shp_file in enumerate(shp_files):
    print('PTSHP_2_TIN: Progress {}/{}, {}'.format(str(index + 1), length, shp_file))
    __point2tin(result_dir, shp_file, 'zvalue')

def tin_to_triangle(tins, result_dir):
  ''' 不规则三角网数据集 转三角形面

  Args:
    tins: 不规则三角网数据集路径数组，使用绝对路径
    result_dir: 输出三角形面到何处
  '''
  length = str(len(tins))
  for index, tin in enumerate(tins):
    print('TIN_2_TRIANGLE: Progress {}/{}, {}'.format(str(index + 1), length, tin))
    tinbasename = os.path.basename(tin)
    result_shp_fullname = os.path.join(result_dir, tinbasename + ".shp")
    arcpy.TinTriangle_3d(tin, result_shp_fullname, "DEGREE", 1, "HILLSHADE 310,45", "tag")

def filter_triangle(triangles_shps, coverage_layer, result_dir):
  ''' 空间选择。使用一个面要素或面 shp 选择生成的三角形面

  Args:
    triangles_shps: 三角形面数据路径数组，要求是绝对路径
    coverage_layer: 一个 shp 文件绝对路径，作为空间选择的覆盖区域
    result_dir: 输出空间选择后的三角形面数据
  '''
  length = str(len(triangles_shps))
  for index, triangle_shp in enumerate(triangles_shps):
    print('FILTER_TRIANGLE: Progress {}/{}, {}'.format(str(index + 1), length, triangle_shp))
  
    source_layer = arcpy.MakeFeatureLayer_management(triangle_shp, "source_" + triangle_shp.replace('.shp', ''))
    arcpy.SelectLayerByLocation_management(source_layer, 'WITHIN_CLEMENTINI', coverage_layer)
    
    newshp_filename = os.path.basename(triangle_shp).replace('.shp', '_selected.shp')
    out_shpfullname = os.path.join(result_dir, newshp_filename)
    
    # 如果输入是具有选定内容的图层，则仅复制所选要素。如果输入是地理数据库要素类或 shapefile，则会复制所有要素。
    arcpy.CopyFeatures_management(source_layer, out_shpfullname)

def __write_shp_geometry_2bin(shp_filefullname, binfile_result_dir):
  shp_filename = os.path.basename(shp_filefullname)
  layer = arcpy.MakeFeatureLayer_management(shp_filefullname, shp_filename)
  bin_file_handle = open(os.path.join(binfile_result_dir, shp_filename.replace('.shp', '.bin')), 'wb')
  statistical_file_handle = open(os.path.join(binfile_result_dir, shp_filename.replace('.shp', '.txt')), 'w')
  zdata = []
  with arcpy.da.SearchCursor(layer, ["SHAPE@"]) as cursor:    
      # 读取 feature
      for feature in cursor:
        # 读取 geometry
        for part in feature[0]: # feature[0] means geometry field.
          for index in range(3):
            # 读取 coords x y z
            point = part[index]
            bin_file_handle.write(struct.pack('f', float(point.X)))
            bin_file_handle.write(struct.pack('f', float(point.Y)))
            bin_file_handle.write(struct.pack('f', float(point.Z)))
            zdata.append(point.Z)
  zmin = min(zdata)
  zmax = max(zdata)
  statistical_file_handle.write("{},{}".format(zmin, zmax))
  statistical_file_handle.close()
  bin_file_handle.flush()
  bin_file_handle.close()

def geometry_to_binfile(shp_names, result_dir):
  ''' shp 中的几何数据转到二进制 VBO

  Args:
    shp_names: shp 文件路径，使用绝对路径
    result_dir: 输出二进制文件到什么地方，使用绝对路径
  '''
  length = str(len(shp_names))
  for index, shp_filefullname in enumerate(shp_names):
    print('TO_BIN: Progress {}/{}, {}'.format(str(index + 1), length, shp_filefullname))
    __write_shp_geometry_2bin(shp_filefullname, result_dir)
