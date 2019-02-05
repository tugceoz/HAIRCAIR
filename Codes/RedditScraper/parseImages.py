#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 29 16:30:38 2019

@author: tozturk
"""

from os import listdir
import pandas as pd
import urllib.request as req
import requests

def find_csv_filenames( path_to_dir, suffix=".csv" ):
    filenames = listdir(path_to_dir)
    return [ filename for filename in filenames if filename.endswith( suffix ) ]

path = '/Users/tozturk/Desktop/Scrapies/top_all/'
filenames = find_csv_filenames(path)
for name in filenames:
  print (name)
opener=req.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
req.install_opener(opener)  
for file in filenames:
    if 'posts' in file:
        data = pd.read_csv(path+file)
    
        picIdentifiers = ['jpg', 'png', 'imgur', 'jpeg', 'tif', 'tiff']

        for i in data.url:
            if 'imgur' in i and 'jpg' not in i:
                print(i)
                i = i + '.jpg'
                print(i)
                try:
                    response = requests.get(i)
                except:
                    pass
                if response.status_code != 200: #could also check == requests.codes.ok
                    continue
                if any(identifier in i for identifier in picIdentifiers):
                    try:
                        req.urlretrieve(i, (path+str(data.id[data.url[data.url == i[:-4]].index[0]]) + '.jpg'))
                    except:
                        pass
            else:
                try:
                    response = requests.get(i)
                except:
                    pass
                if response.status_code != 200: #could also check == requests.codes.ok
                    continue
                if any(identifier in i for identifier in picIdentifiers):
                    try:
                        req.urlretrieve(i, (path+str(data.id[data.url[data.url == i].index[0]]) + '.jpg'))
                    except:
                        pass
print('-- Done!!! -- '*3)