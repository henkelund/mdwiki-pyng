#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Factory module"""

from glob import glob
from os.path import abspath, join
from flask import Flask
import config as default_config
from document import Document

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
    def get_mddoc(cls, path=''):
        """Create a Markdown document from given path"""
        basepath = cls.get_app().config['DOCUMENTS_PATH']
        kwargs = {'filepattern': r'\.md$'}
        return Document(join(basepath, path), **kwargs)

