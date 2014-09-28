#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command line interface module"""

import sys
from getopt import gnu_getopt as getopt
from os import linesep
from flask import request
from factory import Factory
from search import MarkdownIndexer

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Cli:
    """Command line interface class"""

    C_NOTICE  = '0;34'
    C_SUCCESS = '0;32'
    C_ERROR   = '1;31'
    C_WARNING = '1;33'

    def __init__(self, args):
        """Initialize from given arguments"""
        self._command = args.pop(0) if len(args) > 0 else None
        self._args = args

    def _cstr(self, message, color=None):
        """Get a bash color wrapped string"""
        return '\033[%sm%s\033[0m' % (color, message) \
            if sys.stdin.isatty() else message

    def notice(self, message):
        """Print a notice message"""
        print self._cstr(message, self.C_NOTICE)

    def success(self, message):
        """Print a success message"""
        print self._cstr(message, self.C_SUCCESS)

    def warning(self, message):
        """Print a warning message to stderr"""
        sys.stderr.write(self._cstr(message + linesep, self.C_WARNING))

    def error(self, message):
        """Print an error message to stderr"""
        sys.stderr.write(self._cstr(message + linesep, self.C_ERROR))

    def get_options(self, options, long_options=[]):
        """Get command line options"""
        return getopt(self._args, options, long_options)

    def run(self):
        """Execute requested action"""
        action = 'run_%s' % str(self._command).lower()
        if hasattr(self, action):
            try:
                getattr(self, action)()
            except Exception as e:
                self.error(str(e))
                exit(1)
        else:
            self.usage()

    def run_reindex(self):
        """Reindex all documents"""

        app_name = None
        optlist, args = self.get_options('a:', ['app='])
        for key, val in optlist:
            if key in ('-a', '--app'):
                app_name = val

        app = Factory.get_app(app_name)
        with app.test_request_context():
            request.environ['MDWIKI_APP'] = app.name # set current Factory app
            self.notice('Reindexing %s' % app.name)
            indexer = MarkdownIndexer(app.name)
            index = indexer.get_index(True)
            root = Factory.get_mddoc()
            indexer.index_document(root)
            index.optimize()
            self.success('Done')

    def usage(self):
        """Print usage instructions"""
        print """\
Usage: python mdwiki/cli.py ACTION [OPTION]...

Actions:
   reindex        Reindex all documents
    -a, --app=APP specify application/index name
        """

if __name__ == '__main__':
    """Run cli action"""
    Cli(sys.argv[1:]).run()

