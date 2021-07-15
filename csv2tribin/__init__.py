# -*- coding: utf-8 -*-

import os, glob, time
from .data_io import *
from .data_utils import *

def define_and_check_dir(fullname):
  if os.path.exists(fullname) == False:
    os.makedirs(fullname)
  return fullname

def run(csv_dir, coverage_layer_shppath, result_dir = None, csv_filter = '*.csv', open_onend = False):
  ''' 程序主入口

  Args:
    csv_dir: csv 数据文件路径，请使用绝对路径
    coverage_layer_shppath: 覆盖图层 shp 文件绝对路径
    result_dir?: 结果路径，使用绝对路径，若不指定则使用 csv_dir
    csv_filter?: csv 数据文件后缀名，默认 '*.csv'
    open_onend?: 布尔值，指示运行结束后是否打开结果文件夹，默认不打开
  '''
  if os.path.isdir(csv_dir) == False:
    return
  if result_dir == None:
    result_dir = csv_dir

  time_start = time.time()

  csv_files = glob.glob(os.path.join(csv_dir, csv_filter))
  pt_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'to_ptshp'))
  parse_csv_to_pointshp(csv_files, pt_shp_resultdir)
  
  pt_shps = glob.glob(os.path.join(pt_shp_resultdir, '*.shp'))
  tin_resultdir = define_and_check_dir(os.path.join(result_dir, 'tins'))
  pointshp_to_tin(pt_shps, tin_resultdir)

  tins = get_toplevel_dir(tin_resultdir)
  triangle_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'triangles_shp'))
  tin_to_triangle(tins, triangle_shp_resultdir)

  triangle_shps = glob.glob(os.path.join(triangle_shp_resultdir, '*.shp'))
  filtered_triangle_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'filtered_triangles'))
  filter_triangle(triangle_shps, coverage_layer_shppath, filtered_triangle_shp_resultdir)

  filtered_triangle_shps = glob.glob(os.path.join(filtered_triangle_shp_resultdir, '*.shp'))
  finally_resultdir = define_and_check_dir(os.path.join(result_dir, 'finally_result'))
  geometry_to_binfile(filtered_triangle_shps, finally_resultdir, True)

  print('Clean TempFiles ...')

  delete_dir(pt_shp_resultdir, tin_resultdir, triangle_shp_resultdir, filtered_triangle_shp_resultdir)
  time_end=time.time()

  if open_onend:
    os.startfile(finally_resultdir)

  print('Time Cost: {}s.'.format(str(time_end - time_start)))