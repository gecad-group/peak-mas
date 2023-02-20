"""PEAK - Python-based framework for hEterogeneous Agent Communities.

PEAK is a framework for developing communities of heterogeneous agents. 
This communities are multi-agent systems that can coexist and exchange 
resources and information with each other easly. 

isort: skip_file
"""

import logging as _logging

from spade.message import Message
from spade.template import Template

from peak.core import *
from peak.agents import *
from peak.behaviours import *
from peak.properties import *

__author__ = "Bruno Ribeiro"
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.4"

# filtering noisy loggers
_logging.getLogger("aiosasl").setLevel(_logging.ERROR)
_logging.getLogger("spade").setLevel(_logging.ERROR)
_logging.getLogger("muc").setLevel(_logging.ERROR)
_logging.getLogger("StanzaStream").setLevel(_logging.ERROR)
_logging.getLogger("XMLStream").setLevel(_logging.ERROR)
_logging.getLogger("aioopenssl").setLevel(_logging.ERROR)
_logging.getLogger("aioxmpp").setLevel(_logging.ERROR)
_logging.getLogger("asyncio").setLevel(_logging.ERROR)
