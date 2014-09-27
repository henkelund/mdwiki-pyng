#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Factory module"""

from os import environ
from os.path import abspath, join
from glob import glob
from threading import Lock
from flask import Flask, request
import config as default_config
from document import Document
from markdown import MarkdownHtmlRenderer
from search import MarkdownSearcher

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Factory(object):
    """Factory class"""

    _apps = {}
    _lock = Lock()

    @classmethod
    def get_app(cls, name=None):
        """Instantiate Flask app"""
        if not name:
            try:
                name = request.environ.get('MDWIKI_APP')
                if not name:
                    raise RuntimeError('Empty app name')
            except RuntimeError as e: # working outside of request context
                name = 'mdwiki'
        with cls._lock:
            app = cls._apps.get(name)
            if app is None:
                app = Flask(name)
                environ['MDWIKI_APP'] = name # expose app name to config files
                app.config.from_object(default_config)
                for pyfile in glob('config/*.py'):
                    app.config.from_pyfile(abspath(pyfile))
                del environ['MDWIKI_APP']
                cls._apps[name] = app
            return app

    @classmethod
    def get_mddoc(cls, path='', **kwargs):
        """Create a Markdown document from given path"""
        app = cls.get_app()
        base_path = app.config.get('DOCUMENTS_PATH')
        if not 'file_pattern' in kwargs:
            kwargs['file_pattern'] = r'\.md$'
        if not 'content_renderer' in kwargs:
            kwargs['content_renderer'] = MarkdownHtmlRenderer(
                app.config.get('MD_EXTENSIONS'),
                app.config.get('MD_HTML_FLAGS')
            ).render
        return Document(join(base_path, path), **kwargs)

    @classmethod
    def get_searcher(cls, **kwargs):
        """Get searcher instance"""
        app = cls.get_app()
        if not 'index' in kwargs:
            kwargs['index'] = app.name
        if not 'base_path' in kwargs:
            kwargs['base_path'] = app.config.get('DOCUMENTS_PATH')
        if not 'default_limit' in kwargs:
            kwargs['default_limit'] = app.config.get('SEARCH_LIMIT')
        return MarkdownSearcher(**kwargs)

