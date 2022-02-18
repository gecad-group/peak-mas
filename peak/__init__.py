'''
PEAK - Python-based Ecosystem for Agent Communities'''

import logging as _logging

_logging.getLogger('aiosasl').setLevel(_logging.CRITICAL)
_logging.getLogger('spade').setLevel(_logging.CRITICAL)
_logging.getLogger('muc').setLevel(_logging.CRITICAL)
_logging.getLogger('StanzaStream').setLevel(_logging.CRITICAL)
_logging.getLogger('XMLStream').setLevel(_logging.CRITICAL)
_logging.getLogger('aioopenssl').setLevel(_logging.CRITICAL)
_logging.getLogger('aioxmpp').setLevel(_logging.CRITICAL)
_logging.getLogger('StanzaStream').setLevel(_logging.CRITICAL)

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"