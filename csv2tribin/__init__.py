# -*- coding: utf-8 -*-

import os, glob, time
from .data_io import *
from .data_utils import *

def define_and_check_dir(fullname):
  if os.path.exists(fullname) == False:
    os.makedirs(fullname)
  return fullname

def run(
  csv_dir, 
  coverage_layer_shppath,
  result_dir = None, 
  is_clean_temp = True, 
  csv_filter = '*.csv', 
  is_compress = True,
  open_onend = False, 
  skip = []):
  ''' 程序主入口

  Args:
    csv_dir: csv 数据文件路径，请使用绝对路径
    coverage_layer_shppath: 覆盖图层 shp 文件绝对路径
    result_dir?: 结果路径，使用绝对路径，若不指定则使用 csv_dir
    is_clean_temp?: 布尔值，指示是否清除临时数据，默认 True
    csv_filter?: csv 数据文件后缀名，默认 '*.csv'
    is_compress?: 布尔值，指示是否压缩生成的二进制文件，默认 True
    open_onend?: 布尔值，指示运行结束后是否打开结果文件夹，默认不打开
    skip?: list，指示要跳过哪些步骤，默认 []，即不跳步
  '''
  if os.path.isdir(csv_dir) == False:
    return
  if result_dir == None:
    result_dir = csv_dir

  time_start = time.time()

  csv_files = glob.glob(os.path.join(csv_dir, csv_filter))
  pt_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'to_ptshp'))
  
  pt_shps = glob.glob(os.path.join(pt_shp_resultdir, '*.shp'))
  tin_resultdir = define_and_check_dir(os.path.join(result_dir, 'tins'))

  tins = get_toplevel_dir(tin_resultdir)
  triangle_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'triangles_shp'))

  triangle_shps = glob.glob(os.path.join(triangle_shp_resultdir, '*.shp'))
  filtered_triangle_shp_resultdir = define_and_check_dir(os.path.join(result_dir, 'filtered_triangles'))

  filtered_triangle_shps = glob.glob(os.path.join(filtered_triangle_shp_resultdir, '*.shp'))
  finally_resultdir = define_and_check_dir(os.path.join(result_dir, 'finally_result'))
  
  if 1 not in skip:
    parse_csv_to_pointshp(csv_files, pt_shp_resultdir)
  
  if 2 not in skip:
    pointshp_to_tin(pt_shps, tin_resultdir)

  if 3 not in skip:
    tin_to_triangle(tins, triangle_shp_resultdir)

  if 4 not in skip:
    filter_triangle(triangle_shps, coverage_layer_shppath, filtered_triangle_shp_resultdir)

  if 5 not in skip:
    geometry_to_binfile(filtered_triangle_shps, finally_resultdir)
    if is_compress:
      binfiles = glob.glob(os.path.join(finally_resultdir, '*.bin'))
      bin2gz(binfiles)

  if is_clean_temp:
    print('Clean TempFiles ...')
    delete_dir(pt_shp_resultdir, tin_resultdir, triangle_shp_resultdir, filtered_triangle_shp_resultdir)

  time_end=time.time()

  if open_onend:
    os.startfile(finally_resultdir)

  cost = time_end - time_start
  if cost > 60:
    cost = "{}min.".format(cost / 60)
  elif cost > 3600:
    cost = "{}hour.".format(cost / 3600)
  else:
    cost = "{}sec.".format(cost)
  
  print('Time Cost: {}'.format(str(cost)))
