#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document module"""

from os import walk, sep as pathsep
from os.path import isfile, isdir, dirname, basename
import re
from markdown import render_markdown

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Document:
    """Class representing a file system file or directory"""

    TYPE_FILE = 'file'
    TYPE_DIR  = 'dir'
    TYPE_NONE = None

    def __init__(self, filename=None):
        """Initializes a Document instance from a file path"""
        self._errors = []
        if not filename is None:
            self.set_filename(filename)

    def get_errors(self):
        """Get error messages raised by this document"""
        return self._errors

    def set_filename(self, filename):
        """Set the file name of this document"""
        self._filename = filename.rstrip(pathsep)

    def get_filename(self):
        """Get the file name of this document"""
        return self._filename

    def get_dirname(self):
        """Get the directory of this document"""
        if self._filename is None:
            return None
        return dirname(self._filename)

    def get_basename(self):
        """Get the base name of this document"""
        if self._filename is None:
            return None
        return basename(self._filename)

    def get_type(self):
        """Get this documents type of file"""
        if isfile(self._filename):
            return self.TYPE_FILE
        elif isdir(self._filename):
            return self.TYPE_DIR
        return self.TYPE_NONE

    def get_contents(self):
        """Get the contents of this document"""
        ftype = self.get_type()
        if ftype == self.TYPE_DIR:
            entries = []
            mdpattern = re.compile(r'\.md$', re.IGNORECASE)
            for (dirpath, dirnames, filenames) in \
                    walk(self.get_filename(), True, self._walk_err):
                entries.append(dirnames)
                entries.append(
                    [fname for fname in filenames
                        if mdpattern.search(fname)])
                break;
            return entries
        elif ftype == self.TYPE_FILE:
            try:
                with open(self.get_filename()) as fh:
                    return self._parse_contents(fh.read())
            except IOError as e:
                self._errors.append(str(e))
        return None

    def _walk_err(self, err):
        """os.walk error callback"""
        self._errors.append(str(err))

    def _parse_contents(self, contents):
        """Parse file contents"""
        return render_markdown(contents)

    def as_dict(self):
        """Return a dict representation of this document"""
        return {
            'type'     : self.get_type(),
            'dirname'  : self.get_dirname(),
            'basename' : self.get_basename(),
            'contents' : self.get_contents(),
            'errors'   : self.get_errors()
        }

