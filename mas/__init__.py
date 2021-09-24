'''
Multi-Agent System framework based on SPADE framework.

This package is built upon SPADE framework and it has 
the same features as SPADE. Furthermore it adds a new 
XMPP feature, the Multi User Chat (MUC) service.
Agents are now capable of joining group-chats'''


import logging as _logging
import time as _time

from spade.message import Message
from spade.template import Template

from mas.agent import Agent
from mas.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour, FSMBehaviour
import mas.jid
from mas.simulation import Synchronizer, SyncAgent

_logging.getLogger("spade.Agent").setLevel(_logging.ERROR)

__author__ = """Bruno Ribeiro"""
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.0"



def run(*agents):

    for agent in agents:
        agent.start().result()

    def are_alive(agents):
        alive = False
        for agent in agents:
            alive = True if agent.is_alive() else alive
        return alive

    while are_alive(agents):
        try:
            _time.sleep(10)
        except KeyboardInterrupt:
            break

