#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mdwiki controllers"""

from os.path import join
from flask import Flask, jsonify
from mdwiki.config import config
from mdwiki.document import Document

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

app = Flask(__name__)
config(allow_no_value=True).load('config/*.cfg')

@app.route('/file/')
@app.route('/file/<path:path>')
def get_file(path=''):
    """File controller"""
    basepath = config().value('documents_path', 'documents')
    doc = Document(join(basepath, path))
    return jsonify(doc.as_dict())

