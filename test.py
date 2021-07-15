# -*- coding: utf-8 -*-
# @author: xuhuic
# @time: 0715

from csv2tribin import run

if __name__ == '__main__':

  run(
    r'C:\Users\CDCI\Desktop\pytest', 
    r'C:\Users\CDCI\Desktop\1-FullDomain\coverage.shp',
    None,
    '*.txt',
    True
  )
