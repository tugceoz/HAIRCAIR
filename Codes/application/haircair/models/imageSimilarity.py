#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from scipy.spatial import distance

import pandas as pd

def hamming_distance(a,b):
    '''
    compares distance for binary arrays
    returns number of features that are not the same
    '''
    if max(a)>1:
      a[a>0]=1
      b[b>0]=1
    return(distance.hamming(a,b))
    
def find_matches(pred, #features from user selected image
                 features,  #list of features in the collection
                 images, #list of filenames associated with the features
                 dist='cosine' #distance metric - only cosine is good
                 ): 
    '''
    Finds matches for the features of the selected image, 
    according to the distance metric specified.
    Distance metrics use the scipy package
    '''   
    pred = pred.flatten()
    
    nimages = len(features)
    #vectorize cosine similarity
#    sims= inner(pred,collection_features)/norm(pred)/norm(collection_features,axis=1)
    sims = []
    for i in range(0,nimages):
        if dist=='euclidean':
            sims.append(distance.euclidean(pred.flatten(),
                                           features[i].flatten()))
        elif dist=='hamming':
            pred[pred>0]=1
            sims.append(distance.hamming(pred.flatten(),
                                         features[i].flatten()))
        else: #default to cosine
            sims.append(distance.cosine(pred.flatten(),
                                        features[i].flatten()))
    print('max sim = ' +str(max(sims)))
    similar_images=pd.DataFrame({'imgfile':images,
                                 'simscore':sims})
    return(similar_images)


            
