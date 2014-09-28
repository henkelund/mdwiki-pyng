#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Document module"""

from os import walk, sep as pathsep
from os.path import isfile, isdir, dirname, basename, exists
import re

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class Document:
    """Class representing a file system file or directory"""

    TYPE_FILE = 'file'
    TYPE_DIR  = 'dir'
    TYPE_NONE = None

    def __init__(self, filename=None, **kwargs):
        """Initializes a Document instance from a file path"""
        self._errors = []
        self._file_pattern = re.compile(kwargs['file_pattern'], re.IGNORECASE) \
            if 'file_pattern' in kwargs else None
        self._content_renderer = kwargs['content_renderer'] \
            if 'content_renderer' in kwargs else None
        self._filename = None
        if not filename is None:
            self.set_filename(filename)

    def get_errors(self):
        """Get error messages raised by this document"""
        return self._errors

    def set_filename(self, filename):
        """Set the file name of this document"""
        if not exists(filename):
            self._filename = None
            self._errors.append('File not found: %s' % filename)
        elif self._file_pattern is None \
                or self._file_pattern.search(filename) \
                or isdir(filename):
            self._filename = filename.rstrip(pathsep)
        else:
            self._filename = None
            self._errors.append('Unsupported file type: %s' % filename)
        return self

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
        if self._filename is None:
            return self.TYPE_NONE
        elif isfile(self._filename):
            return self.TYPE_FILE
        elif isdir(self._filename):
            return self.TYPE_DIR
        return self.TYPE_NONE

    def get_raw_file_contents(self):
        """Get contents of this Document if it is a file, None otherwise"""
        try:
            with open(self._filename) as fh:
                return fh.read()
        except IOError as e:
            self._errors.append(str(e))
        return None

    def get_file_contents(self):
        """Get processed contents of this Documents if it is a file"""
        text = self.get_raw_file_contents()
        if text is not None and self._content_renderer is not None:
            text = self._content_renderer(text, self.get_basename())
        return text

    def get_contents(self):
        """Get the contents of this document"""
        ftype = self.get_type()
        if ftype == self.TYPE_DIR:
            for (dirpath, dirnames, filenames) in \
                    walk(self.get_filename(), True, self._walk_err):
                return (
                    dirnames,
                    [fname for fname in filenames
                        if self._file_pattern is None
                            or self._file_pattern.search(fname)]
                )
            return ((), ())
        elif ftype == self.TYPE_FILE:
            return self.get_file_contents()
        return None

    def _walk_err(self, err):
        """os.walk error callback"""
        self._errors.append(str(err))

    def as_dict(self):
        """Return a dict representation of this document"""
        return {
            'type'     : self.get_type(),
            'dirname'  : self.get_dirname(),
            'basename' : self.get_basename(),
            'contents' : self.get_contents(),
            'errors'   : self.get_errors()
        }

