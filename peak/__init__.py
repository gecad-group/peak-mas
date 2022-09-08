"""
PEAK - Python-based Ecosystem for Agent Communities"""

import logging as _logging

_logging.getLogger("aiosasl").setLevel(_logging.ERROR)
_logging.getLogger("spade").setLevel(_logging.ERROR)
_logging.getLogger("muc").setLevel(_logging.ERROR)
_logging.getLogger("StanzaStream").setLevel(_logging.ERROR)
_logging.getLogger("XMLStream").setLevel(_logging.ERROR)
_logging.getLogger("aioopenssl").setLevel(_logging.ERROR)
_logging.getLogger("aioxmpp").setLevel(_logging.ERROR)
_logging.getLogger("asyncio").setLevel(_logging.ERROR)


__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"
