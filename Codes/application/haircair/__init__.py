#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)
app.config.from_object(__name__) 
app.config.update(dict(
        UPLOAD_FOLDER = "haircair/static/img/tmp/",
        DATA_FOLDER = "haircair/models/",
        ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
))

from haircair import Flask_Test
