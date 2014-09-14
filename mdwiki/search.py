#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Search module"""

import os.path
import re
import whoosh.index
import whoosh.fields
import whoosh.analysis
import whoosh.qparser
import misaka as m
from flask import Markup

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

index_dir = os.path.join('var', 'index')
index_name = 'mdwiki'

class CaptureRenderer(m.BaseRenderer):
    """Markdown renderer for capturing high-weight content"""

    def setup(self):
        """Define capture containers"""
        super(CaptureRenderer, self).setup()
        self._headers = []

    def header(self, text, level):
        """Capture header text (renderer callback)"""
        self._headers.append((text, level))
        return text

    def get_headers(self):
        """Get captured header texts"""
        headers = []
        for text, level in self._headers:
            headers.append(text)
        return headers

    def get_title(self):
        """Get the first lowest level header text"""
        title = (None, 7)
        for text, level in self._headers:
            if level < title[1]:
                title = (text, level)
        return title[0]

class MarkdownIndexer:
    """Markdown document indexer class"""

    def get_index(self, clear=False):
        """Retrieve (and create if needed) index instance"""
        if not os.path.isdir(index_dir):
            os.makedirs(index_dir, 0777)
        if not whoosh.index.exists_in(index_dir, index_name) or clear:
            return whoosh.index.create_in(
                index_dir,
                self.get_schema(),
                index_name
            )
        else:
            return whoosh.index.open_dir(index_dir, index_name)

    def get_schema(self):
        """Retrieve index definition"""
        return whoosh.fields.Schema(
            title=whoosh.fields.TEXT(
                stored=True,
                field_boost=2.0
            ),
            path=whoosh.fields.ID(
                stored=True
            ),
            content=whoosh.fields.TEXT(
                stored=True,
                analyzer=whoosh.analysis.StemmingAnalyzer()
            )
        )

    def create_record(self, document):
        """Extract index data from given document"""
        if not document.get_type() is document.TYPE_FILE:
            return None

        raw_contents = document.get_raw_file_contents()
        if not isinstance(raw_contents, basestring):
            return None

        # Find important portions of the document
        capture = CaptureRenderer()
        m.Markdown(
            capture,
            extensions=m.EXT_FENCED_CODE
        ).render(raw_contents)

        return {
            'title': unicode(
                capture.get_title() or \
                    re.sub(
                        r'\.md$',
                        '',
                        document.get_basename(),
                        1,
                        re.IGNORECASE
                    )
            ),
            'path': unicode(
                document.get_filename()
            ),
            'content': unicode(
                Markup(document.get_file_contents()).striptags()
            )
        }

    def index_document(self, document):
        """Index a single document"""
        # Recursively collect records
        records = []
        if document.get_type() is document.TYPE_DIR:
            dirname = document.get_filename()
            subdirs, files = document.get_contents()
            for subdir in subdirs:
                document.set_filename(os.path.join(dirname, subdir))
                self.index_document(document)
            for filename in files:
                document.set_filename(os.path.join(dirname, filename))
                record = self.create_record(document)
                if record is not None:
                    records.append(record)

        if len(records) == 0:
            return

        # Store records
        writer = self.get_index().writer()
        for record in records:
            writer.add_document(**record)
        writer.commit()

class MarkdownSearcher:
    """Markdown document search class"""

    def __init__(self, **kwargs):
        """Initialize index instance"""
        self._index = MarkdownIndexer().get_index()
        self._base_path = kwargs['base_path'] \
            if 'base_path' in kwargs else None
        self._default_limit = kwargs['default_limit'] \
            if 'default_limit' in kwargs else None

    def _get_searcher(self):
        """Retrieve searcher instance"""
        return self._index.searcher()

    def _get_query_parser(self):
        """Create a multi field, or-conditioned query parser"""
        return whoosh.qparser.MultifieldParser(
            ('title', 'content'),
            self._index.schema,
            plugins=[whoosh.qparser.PrefixPlugin],
            group=whoosh.qparser.OrGroup.factory(0.9)
        )

    def _get_base_path_pattern(self):
        """Get base path pattern to strip from search hits"""
        if self._base_path is not None:
            return '^%s' % re.escape(self._base_path)
        return None

    def search(self, text, **kwargs):
        """Search for documents matching given text"""
        results = []
        path_pattern = self._get_base_path_pattern()
        if not 'limit' in kwargs and self._default_limit is not None:
            kwargs['limit'] = self._default_limit
        query = self._get_query_parser().parse(unicode(text))
        with self._get_searcher() as searcher:
            for hit in searcher.search(query, **kwargs):
                filename = re.sub(path_pattern, '', hit['path'], 1) \
                    if path_pattern is not None else hit['path']
                results.append({
                    'title':      hit['title'],
                    'file':       filename,
                    'highlights': hit.highlights('content')
                })
        return results

