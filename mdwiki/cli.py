#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Command line interface module"""

import sys
import getopt
from factory import Factory
from search import MarkdownIndexer

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Cli:
    """Command line interface class"""

    def __init__(self, args):
        """Initialize from given arguments"""
        self._command = args.pop(0) if len(args) > 0 else None
        self._args = args

    def run(self):
        """Execute requested action"""
        action = 'run_%s' % str(self._command).lower()
        if hasattr(self, action):
            getattr(self, action)()
        else:
            self.usage()

    def run_reindex(self):
        """Reindex all documents"""
        print 'Reindexing all documents..'
        indexer = MarkdownIndexer()
        index = indexer.get_index(True)
        root = Factory.get_mddoc()
        indexer.index_document(root)
        index.optimize()
        print 'Done'

    def usage(self):
        """Print usage instructions"""
        print """\
Usage: python mdwiki/cli.py ACTION [OPTION]...

Actions:
   reindex    Reindex all documents
        """

if __name__ == '__main__':
    """Run cli action"""
    Cli(sys.argv[1:]).run()

