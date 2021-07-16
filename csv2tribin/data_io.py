# -*- coding: utf-8 -*-
import gzip, shutil, os, json, sys, time

def gz_compress(path):
  ''' 压缩一个文件。

  压缩后的文件名会多一个 `.gz` 后缀，例如压缩 `foo.bin`，最终结果是 `foo.bin.gz`

  Args
    `path`: 文件的绝对路径。例如 `C:/nobel.txt`

  '''
  with open(path, 'rb') as f:
    with gzip.open(path + '.gz', 'wb') as gzfile:
      gzfile.writelines(f)

def delete_dir(*dirs):
  ''' 递归删除文件夹。

  Args:
    *dirs: 文件夹绝对路径集合
  '''
  try:
    for dir in dirs:
      if os.path.exists(dir):
        shutil.rmtree(dir)
  except:
    info = "有部分文件夹可能被占用，稍后请手动删除不需要的文件夹"
    info = info.decode('utf-8').encode(sys.getfilesystemencoding())
    print(info)


def bin2gz(files):
  '''原处生成gz同名压缩文件并输出文件名列表，存储到json文件中

  Args:
    files: 文件路径数组，用绝对路径
  '''
  ticks = time.time()
  namelist = {
    generateTime: ticks,
    names: []
  }
  for bin_full_filename in files:
    gz_compress(bin_full_filename)
    dirname, basename = os.path.split(bin_full_filename)
    basename_withoutext = basename.replace('.bin', '')
    namelist.names.append(basename_withoutext)
    with open(os.path.join(dirname, 'namelist.json'), 'w') as json_handle:
      json.dump(namelist, json_handle)

def get_toplevel_dir(root_dir):
  names = []
  for name in [ name for name in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, name))]:
    names.append(os.path.join(root_dir, name))
  return names
