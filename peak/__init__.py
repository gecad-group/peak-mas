'''
PEAK - Python-based Ecosystem for Agent Communities'''

import logging as _logging
import sys

_logging.getLogger('aiosasl').setLevel(_logging.ERROR)
_logging.getLogger('spade').setLevel(_logging.ERROR)
_logging.getLogger('muc').setLevel(_logging.ERROR)
_logging.getLogger('StanzaStream').setLevel(_logging.ERROR)
_logging.getLogger('XMLStream').setLevel(_logging.ERROR)
_logging.getLogger('aioopenssl').setLevel(_logging.ERROR)
_logging.getLogger('aioxmpp').setLevel(_logging.ERROR)
_logging.getLogger('asyncio').setLevel(_logging.ERROR)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    _logging.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"