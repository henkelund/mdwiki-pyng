#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mdwiki controllers"""

from os.path import join
from flask import jsonify
from mdwiki.factory import Factory
from mdwiki.document import Document

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

app = Factory.get_app()

@app.route('/file/')
@app.route('/file/<path:path>')
def get_file(path=''):
    """File controller"""
    basepath = app.config['DOCUMENTS_PATH']
    doc = Document(
        join(basepath, path),
        filepattern=r'\.md$'
    )
    return jsonify(doc.as_dict())

