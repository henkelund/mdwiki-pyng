#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mdwiki controllers"""

from flask import jsonify
from factory import Factory
from search import MarkdownSearcher

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

app = Factory.get_app()

@app.route('/file/')
@app.route('/file/<path:path>')
def get_file(path=''):
    """File controller"""
    doc = Factory.get_mddoc(path)
    return jsonify(doc.as_dict())

@app.route('/search/<path:query>')
def get_search_result(query):
    """Search controller"""
    result = MarkdownSearcher().search(query + '*')
    return jsonify({'hits': result})

