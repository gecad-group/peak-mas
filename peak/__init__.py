"""PEAK - Python-based framework for hEterogeneous Agent Communities"""

import logging as _logging

from spade.message import Message
from spade.template import Template

from peak.agent import *
from peak.behaviours import *
from peak.jid import *
from peak.properties import *
from peak.simulation import *

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"


_logging.getLogger("aiosasl").setLevel(_logging.ERROR)
_logging.getLogger("spade").setLevel(_logging.ERROR)
_logging.getLogger("muc").setLevel(_logging.ERROR)
_logging.getLogger("StanzaStream").setLevel(_logging.ERROR)
_logging.getLogger("XMLStream").setLevel(_logging.ERROR)
_logging.getLogger("aioopenssl").setLevel(_logging.ERROR)
_logging.getLogger("aioxmpp").setLevel(_logging.ERROR)
_logging.getLogger("asyncio").setLevel(_logging.ERROR)
