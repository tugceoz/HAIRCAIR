#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 15:19:48 2019

@author: tozturk
"""

from keras import applications
from keras.applications.resnet50 import preprocess_input
#from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image as kimage
import numpy as np
import glob, os

imagespath= "/Users/tozturk/Desktop/Images"
os.chdir(imagespath)
images=sorted(glob.glob("*.jpg"))
nimages=len(images)

#include the top, then pop according to the chosen neural net
model = applications.resnet50.ResNet50(include_top=True, weights='imagenet')

#For all preTrained models, remove the classification layer
model.layers.pop()
#if VGG, remove the next fully connected layer as well
#model.layers.pop()
#fix the output of the model
model.outputs = [model.layers[-1].output]

feats=[]
#image size 224 for all but 299 for xception
for imgname in images:
    x = kimage.load_img(imgname, target_size=(224, 224))
    x = kimage.img_to_array(x)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    feats.append(model.predict(x))

features = np.concatenate(feats,axis=0)
np.save('Resnet_features',feats)
features[features>0]=1
np.save('Resnet_features_binary',feats)
