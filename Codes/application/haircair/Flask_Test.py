#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

import flask
import numpy as np
import tensorflow as tf
import pandas as pd

from werkzeug.utils import secure_filename
from PIL import ExifTags, Image
from keras import applications
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image as kimage
import spacy
#from haircair.models.imagenet_utils import preprocess_input
#from haircair.models.plot_utils import plot_query_answer
#from haircair.models.sort_utils import find_topk_unique
#from haircair.models.kNN import kNN
#from haircair.models.tSNE import plot_tsne

from haircair import app
from haircair.models.imageSimilarity import find_matches


features = np.load(os.path.join(app.config['DATA_FOLDER'],
                                           'VGG16_features.npy'))
images = pd.read_csv(os.path.join(app.config['DATA_FOLDER'],
                                          'images.csv'))
comments = pd.read_csv(os.path.join(app.config['DATA_FOLDER'],
                                   'CommentPicPairs.csv'))
nlp = spacy.load(os.path.join(app.config['DATA_FOLDER'],'newModel'))
                 
app.secret_key = 'tugce'

graph = tf.get_default_graph()

#include the top, then pop according to the chosen neural net
model = applications.vgg16.VGG16(include_top=True, weights='imagenet')

#For all preTrained models, remove the classification layer
model.layers.pop()
#if VGG, remove the next fully connected layer as well
model.layers.pop()
#fix the output of the model
model.outputs = [model.layers[-1].output]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def autorotate_image(filepath):
    
    image=Image.open(filepath)
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation]=='Orientation':
                break
            exif=dict(image._getexif().items())
    
        if exif[orientation] == 3:
            print('ROTATING 180')
            image=image.rotate(180, expand=True)
        elif exif[orientation] == 6:
            print('ROTATING 270')
            image=image.rotate(270, expand=True)
        elif exif[orientation] == 8:
            print('ROTATING 90')
            image=image.rotate(90, expand=True)
        image.save(filepath)
        image.close()
    except (AttributeError, KeyError, IndexError):
    # cases: image don't have getexif   
        pass
    return(image)
    
@app.route('/',  methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
        # Get method type
    method = flask.request.method
    print(method)


    if method == 'GET':
        return flask.render_template('index.html')
    
    if method == 'POST':
        # No file found in the POST submission
        if 'file' not in flask.request.files:
            print("FAIL")
            return flask.redirect(flask.request.url)

        # File was found
        file = flask.request.files['file']
        if file and allowed_file(file.filename):


            img_file = flask.request.files.get('file')
            
            print('Rotated!')
            #secure file name so stop hackers
            img_name = secure_filename(img_file.filename)

            # Write image to tmp folder so it can be shown on the next page 
            imgurl=os.path.join(app.config['UPLOAD_FOLDER'], img_name)
            file.save(imgurl)
            #check and rotate cellphone images
            img_file = autorotate_image(imgurl)
                
            #load image for processing through the model
            img = kimage.load_img(imgurl, target_size=(224, 224))
            img = kimage.img_to_array(img)
            img = np.expand_dims(img, axis=0)  
            
            #there's an issue with the model losing track of the graph
            #I found this fix by searching for the error I was getting
            #see above
            global graph
            with graph.as_default():
                pred=model.predict(img)
            matches=find_matches(pred, features, 
                                 images,dist='cosine')
            
            showresults=images.set_index('imgfile',drop=False).join(matches.set_index('imgfile'))
            showresults.sort_values(by='simscore',ascending=True,inplace=True)
            
            original_url = img_name

            imgfiles = showresults['imgfile']
            df= comments[comments['imgfile'] == imgfiles[0]]
            text1 = str(df.body)
            doc1 = nlp(text1)
            if not doc1.ents:
                product1 = 'N/A'
            else:
                product1 = doc1.ents[0].text
            df2= comments[comments['imgfile'] == imgfiles[1]]
            text2 = str(df2.body)
            doc2 = nlp(text2)
            if not doc2.ents:
                product2 = 'N/A'
            else:
                product2 = doc2.ents[0].text
            df3= comments[comments['imgfile'] == imgfiles[2]]
            text3 = str(df3.body)
            doc3 = nlp(text3)
            if not doc3.ents:
                product3 = 'N/A'
            else:
                product3 = doc3.ents[0].text
            df4= comments[comments['imgfile'] == imgfiles[3]]
            text4 = str(df4.body)
            doc4 = nlp(text4)
            if not doc4.ents:
                product4 = 'N/A'
            else:
                product4 = doc4.ents[0].text
            df5= comments[comments['imgfile'] == imgfiles[4]]
            text5 = str(df5.body)
            doc5 = nlp(text5)
            if not doc5.ents:
                product5 = 'N/A'
            else:
                product5 = doc5.ents[0].text
#f_html = df.to_html()  # use pandas method to auto generate html
            return flask.render_template('results.html',matches=showresults,original=original_url, product1=product1,product2=product2,product3=product3,product4=product4,product5=product5)
        flask.flash('Upload only image files')

        
        return flask.redirect(flask.request.url)
