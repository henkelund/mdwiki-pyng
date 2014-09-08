#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Config module"""

from glob import glob
from ConfigParser import SafeConfigParser

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

instance = None

class Config(SafeConfigParser):
    """Config class"""

    def value(self, key, default=None, section='global', *args):
        """Get config value by key or 'default' if not found"""
        value = default
        try:
            value = self.get(section, key, *args)
        except Exception:
            pass
        return value

    def load(self, filepattern):
        """Load configuration from files matching 'filepattern'"""
        for cfg in glob(filepattern):
            self.read(cfg)
        return self

def config(*args, **kargs):
    """Return a global Config class instance"""
    global instance
    if instance is None:
        instance = Config(*args, **kargs)
    return instance

