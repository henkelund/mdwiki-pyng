#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Markdown parser module"""

import misaka
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from flask import escape

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

class PygmentsRenderer(misaka.HtmlRenderer, misaka.SmartyPants):
    """Custom Markdown renderer using Pygments for syntax highlighting"""

    def block_code(self, text, lang):
        """Markdown code block render function"""
        if not lang:
            return '\n<pre><code>%s</code></pre>\n' % \
                escape(text.strip())
        lexer = get_lexer_by_name(lang, stripall=True, startinline=True)
        formatter = HtmlFormatter(cssclass='highlight highlight-' + lang)
        return highlight(text, lexer, formatter)

def render_markdown(mdstring):
    """Render HTML from a Markdown string"""
    renderer = PygmentsRenderer()
    md = misaka.Markdown(
        renderer,
        extensions=misaka.EXT_FENCED_CODE | misaka.EXT_NO_INTRA_EMPHASIS
    )
    return md.render(mdstring)

