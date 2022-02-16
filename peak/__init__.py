'''
PEAK - Python-based Ecosystem for Agent Communities'''

import logging as _logging

_logging.getLogger('aiosasl').setLevel(_logging.CRITICAL)
_logging.getLogger('spade').setLevel(_logging.CRITICAL)
_logging.getLogger('agent').setLevel(_logging.CRITICAL)

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"