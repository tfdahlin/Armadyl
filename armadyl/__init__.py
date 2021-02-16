# -*- coding: utf-8 -*-
# flake8: noqa: F401
"""
Armadyl: a lightweight Python web framework.
"""
__title__ = 'armadyl'
__author__ = 'Taylor Fox Dahlin'
__license__ = 'MIT License'
__copyright__ = 'Copyright 2021 Taylor Fox Dahlin'

# Imports here will be available via `import Armadyl.<var>`
from .version import __version__
from pycnic.core import WSGI
from .base import BaseHandler, JsonEndpoint, ServeFile
