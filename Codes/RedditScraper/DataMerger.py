#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 11:59:02 2019

@author: tozturk
"""

from os import listdir
import pandas as pd


def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]
paths = ['/Users/tozturk/Desktop/Scrapies/top_day/', '/Users/tozturk/Desktop/Scrapies/top_week/',
        '/Users/tozturk/Desktop/Scrapies/top_month/', '/Users/tozturk/Desktop/Scrapies/top_year/',
        '/Users/tozturk/Desktop/Scrapies/top_all/']

bigDataList = pd.DataFrame([])
for path in paths:
    filenames = find_csv_filenames(path)
    for file in filenames:
        if ('comments' in file or 'replies' in file):
            data = pd.read_csv(path+file)
            data['rootFile'] = file
            data['path'] = path
            bigDataList = bigDataList.append(data, ignore_index = True)

bigData = pd.concat([bigDataList])
bigData.to_csv('TextData.csv')

