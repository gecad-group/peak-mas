'''
Multi-Agent System framework based on SPADE framework.

This package is built upon SPADE framework and it has 
the same features as SPADE. Furthermore it adds a new 
XMPP feature, the Multi User Chat (MUC) service.
Agents are now capable of joining group-chats'''

import logging as _logging
import sys as _sys

from spade.message import Message
from spade.template import Template

from mas.agent import Agent
from mas.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour
from mas.jid import *
from mas.simulation import Synchronizer, SyncAgent
from mas.properties import Property, Properties

_logging.getLogger("spade.Agent").setLevel(_logging.ERROR)

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"




