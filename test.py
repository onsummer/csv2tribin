# -*- coding: utf-8 -*-
# @author: xuhuic
# @time: 0723

from csv2tribin import run

if __name__ == '__main__':

  run(
    r'D:\WorkingInDCI\01-Macao3D\stormdata\shanzhu', 
    r'D:\WorkingInDCI\01-Macao3D\stormdata\shanzhu\masklayer.shp',
    None,
    False,
    '*.txt',
    True,
    True,
    [1, 2, 3, 4]
  )
