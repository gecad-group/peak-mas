"""PEAK - Python-based framework for hEterogeneous Agent Communities"""

import logging as _logging

from spade.message import Message
from spade.template import Template

from peak.agent import Agent
from peak.behaviour.base import (
    CyclicBehaviour,
    FSMBehaviour,
    OneShotBehaviour,
    PeriodicBehaviour,
)
from peak.behaviour.utils import *
from peak.jid import *
from peak.properties import Properties, Property
from peak.simulation import SyncAgent, Synchronizer

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
