#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Auth module"""

from functools import wraps
from flask import request, Response
from factory import Factory

__author__ = 'Henrik Hedelund'
__copyright__ = 'Copyright 2014, Henrik Hedelund'
__license__ = 'AGPL 3'
__email__ = 'henke.hedelund@gmail.com'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Login Required',
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'}
    )

def requires_auth(f):
    """Authentiction route wrapper"""
    @wraps(f)
    def decorated(*args, **kwargs):
        config = Factory.get_app().config
        username = config.get('USERNAME')
        password = config.get('PASSWORD')
        if username and password:
            auth = request.authorization
            if not auth \
                    or auth.username != username \
                    or auth.password != password:
                return authenticate()
        return f(*args, **kwargs)
    return decorated

