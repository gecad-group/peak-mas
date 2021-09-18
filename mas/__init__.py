from mas.base import MASAgent as Agent, run
from mas.simulation import Synchronizer, SyncAgent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour, PeriodicBehaviour
from spade.message import Message
from spade.template import Template


if __name__ == '__main__':
    import sys
    import mas.config
    mas.config(sys.argv)
