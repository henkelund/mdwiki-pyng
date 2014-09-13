#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Markdown parser module"""

import misaka as m
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from flask import escape

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

misaka_extensions = {
    # Do not parse emphasis inside of words
    'no-intra-emphasis': m.EXT_NO_INTRA_EMPHASIS,
    # Parse PHP-Markdown tables
    'tables':            m.EXT_TABLES,
    # Parse fenced code blocks, PHP-Markdown style
    'fenced-code':       m.EXT_FENCED_CODE,
    # Parse links even when they are not enclosed in <> characters
    'autolink':          m.EXT_AUTOLINK,
    # Parse strikethrough, PHP-Markdown style
    'strikethrough':     m.EXT_STRIKETHROUGH,
    # HTML blocks do not require to be surrounded by an empty line
    'lax-html-blocks':   m.EXT_LAX_HTML_BLOCKS,
    # A space is always required between a hash and a header name
    'space-headers':     m.EXT_SPACE_HEADERS,
    # Parse superscripts after the ^ character
    'superscript':       m.EXT_SUPERSCRIPT
}

misaka_html_flags = {
    # Do not allow any user-inputted HTML in the output
    'skip-html':   m.HTML_SKIP_HTML,
    # Do not generate any <style> tags
    'skip-style':  m.HTML_SKIP_STYLE,
    # Do not generate any <img> tags
    'skip-images': m.HTML_SKIP_IMAGES,
    # Do not generate any <a> tags
    'skip-links':  m.HTML_SKIP_LINKS,
    # Unused
    'expand-tabs': m.HTML_EXPAND_TABS,
    # Only generate links for protocols which are considered safe
    'safelink':    m.HTML_SAFELINK,
    # Add HTML anchors to each header in the output HTML
    'toc':         m.HTML_TOC,
    # Translate newlines to HTML <br> tags inside paragraphs 
    'hard_wrap':   m.HTML_HARD_WRAP,
    # Output XHTML-conformant tags
    'use-xhtml':   m.HTML_USE_XHTML,
    # Escape all HTML tags
    'escape':      m.HTML_ESCAPE
}

class SyntaxHighlightRenderer(m.HtmlRenderer, m.SmartyPants):
    """Custom Markdown renderer using Pygments for syntax highlighting"""

    def block_code(self, text, lang):
        """Markdown code block render function"""
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                escape(text.strip())
        lexer = get_lexer_by_name(lang, stripall=True, startinline=True)
        formatter = HtmlFormatter(cssclass='highlight highlight-' + lang)
        return highlight(text, lexer, formatter)

class MarkdownHtmlRenderer:
    """Markdown to HTML renderer class"""

    def __init__(self, extensions=(), html_flags=()):
        """Initialize parser and renderer"""
        md_kwargs = {}
        renderer_flags = 0

        # Translate extension flags
        for ext in extensions:
            if ext in misaka_extensions:
                if not 'extensions' in md_kwargs:
                    md_kwargs['extensions'] = misaka_extensions[ext]
                else:
                    md_kwargs['extensions'] |= misaka_extensions[ext]

        # Translate renderer flags
        for flag in html_flags:
            if flag in misaka_html_flags:
                renderer_flags |= misaka_html_flags[flag]

        renderer = SyntaxHighlightRenderer(renderer_flags)
        self._markdown = m.Markdown(renderer, **md_kwargs)

    def render(self, text, filename=None):
        """Render Markdown text as HTML"""
        return self._markdown.render(text)

