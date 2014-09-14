#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Factory module"""

from glob import glob
from os.path import abspath, join
from flask import Flask
import config as default_config
from document import Document
from markdown import MarkdownHtmlRenderer
from search import MarkdownSearcher

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Factory:
    """Factory class"""

    _app = None

    @classmethod
    def get_app(cls):
        """Instantiate Flask app"""
        if cls._app is None:
            cls._app = Flask('mdwiki')
            cls._app.config.from_object(default_config)
            for pyfile in glob('config/*.py'):
                cls._app.config.from_pyfile(abspath(pyfile))
        return cls._app

    @classmethod
    def get_mddoc(cls, path='', **kwargs):
        """Create a Markdown document from given path"""
        config = cls.get_app().config
        base_path = config['DOCUMENTS_PATH']
        if not 'file_pattern' in kwargs:
            kwargs['file_pattern'] = r'\.md$'
        if not 'content_renderer' in kwargs:
            kwargs['content_renderer'] = MarkdownHtmlRenderer(
                config['MD_EXTENSIONS'],
                config['MD_HTML_FLAGS']
            ).render
        return Document(join(base_path, path), **kwargs)

    @classmethod
    def get_searcher(cls, **kwargs):
        """Get searcher instance"""
        config = cls.get_app().config
        if not 'base_path' in kwargs:
            kwargs['base_path'] = config['DOCUMENTS_PATH']
        if not 'default_limit' in kwargs:
            kwargs['default_limit'] = config['SEARCH_LIMIT']
        return MarkdownSearcher(**kwargs)

