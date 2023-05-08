"""PEAK - Python-based framework for heterogeneous agent communities.

PEAK is a framework for developing communities of heterogeneous agents. 
This communities are multi-agent systems that can coexist and exchange 
resources and information with each other easly. 

isort: skip_file
"""

import logging

from spade.message import Message
from spade.template import Template

from peak.core import *
from peak.agents import *
from peak.behaviours import *

logging.getLogger(__name__).addHandler(logging.NullHandler())

__author__ = "Bruno Ribeiro"
__email__ = "brgri@isep.ipp.pt"
__version__ = "1.0.7"
