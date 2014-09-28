#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""mdwiki controllers"""

from flask import jsonify
from factory import Factory

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'


class Dispatcher(object):
    """Application dispatcher class"""

    def __init__(self):
        """Define contoller action routes"""
        self._routes = (
            ('/file/', 'file_action'),
            ('/file/<path:path>','file_action'),
            ('/search/<path:query>', 'search_action')
        )

    def _attach_routes(self, app):
        """Attach controller actions to given app"""
        for rule, endpoint in self._routes:
            app.add_url_rule(rule, endpoint, getattr(self, endpoint))

    def file_action(self, path=''):
        """File controller"""
        return jsonify(Factory.get_mddoc_data(path, True))

    def search_action(self, query):
        """Search controller"""
        searcher = Factory.get_searcher()
        result = searcher.search(query + '*')
        return jsonify({
            'hits': result,
            'correction': searcher.correct(query)
        })

    def __call__(self, environ, start_response):
        """Proxy callable for app instance"""
        app = Factory.get_app(environ.get('MDWIKI_APP'))
        if not app.got_first_request:
            self._attach_routes(app)
        return app(environ, start_response)

app = Dispatcher()

