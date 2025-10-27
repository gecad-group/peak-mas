# PEAK: Python-based framework for heterogenous agent communities

[![DOI](https://img.shields.io/badge/DOI-10.1007%2F978--3--031--18050--7__7-blue)](http://dx.doi.org/10.1016/j.softx.2025.102190)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peak-mas)](https://pypi.org/project/peak-mas/)
[![PyPI](https://img.shields.io/pypi/v/peak-mas)](https://pypi.org/project/peak-mas/)
[![GitHub](https://img.shields.io/github/license/gecad-group/peak-mas)](https://github.com/gecad-group/peak-mas)
[![powered by](https://img.shields.io/static/v1?label=powered%20by&message=GECAD&color=177985&labelColor=de5d4a)](https://www.gecad.isep.ipp.pt/GECAD/Pages/Presentation/Home.aspx)
[![code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![imports isort](https://img.shields.io/static/v1?label=imports&message=isort&color=blue&labelColor=orange)](https://pycqa.github.io/isort/)

PEAK is a software framework that can help you develop classic multi-agent systems in Python (3.9.6). PEAK has its roots in <a href="https://spade-mas.readthedocs.io/en/latest/" target="_blank">SPADE</a> and is distinguished by helping you streamline agent development through the use of agent configuration files, a dedicated command line interface, and available pre defined behaviors and agents. Some functionalities of SPADE were tweaked to make it easier to develop agents. 

## Features

- Run your agents in individual processes
- Use the command line interface to run your agents
- Configure your multi-agent system execution with YAML
- Develop your agents using the behavior-driven development paradigm
- Distribute your PEAK system between different machines
- It uses Extensible Messaging and Presence Protocol (XMPP) for communication
- Create agent group chats where you can talk with your agents
- Make your agents data easily available to dashboards


## Installation

Install PEAK in your Python (3.9.6) environment using the following command:

```bash
$ pip install peak-mas
```

## Example

Run your first agent by saving the following code in a file called `agent.py`.

```python 
from peak import Agent, OneShotBehaviour, getLogger

logger = getLogger(__name__)

class HelloWorld(OneShotBehaviour):
    async def run(self):
        logger.info("Hello World!!!")
        await self.agent.stop()

class agent(Agent):
    async def setup(self):
        self.add_behaviour(HelloWorld())
```

Chose a XMPP server (e.g. localhost or chose one from [here](https://list.jabber.at/)) and execute your agent in the terminal:

```bash 
$ peak run path/to/agent.py -j agent@localhost
```

<a href="http://www.gecad.isep.ipp.pt/peak" target="_blank">See the docs for more info.</a>


## Support

Use the <a href="https://github.com/gecad-group/peak-mas/discussions" target="_blank">Discussion</a> page if you have any questions or ideas you would like so see implemented.
To alert an issue or a bug please post in the <a href="https://github.com/gecad-group/peak-mas/issues" target="_blank">Issues</a> page.

## Scientific Publications

- Ribeiro, B., Dias, D., Gomes, L., & Vale, Z. (2025). PEAK: Python-based framework for heterogeneous agent communities. SoftwareX, 30, 102190. https://doi.org/10.1016/j.softx.2025.102190
- Pereira H, Ribeiro B, Gomes L, Vale Z. Smart Grid Ecosystem Modeling Using a Novel Framework for Heterogenous Agent Communities. Sustainability. 2022; 14(23):15983. https://doi.org/10.3390/su142315983
- Silva C, Faria P, Ribeiro B, Gomes L, Vale Z. Demand Response Contextual Remuneration of Prosumers with Distributed Storage. Sensors. 2022; 22(22):8877. https://doi.org/10.3390/s22228877


## Contribute

Pull requests are welcome. For major changes, please open a discussion first to discuss what you would like to change.

The examples are used as a form of testing the framework. So please make sure to update the examples as appropriate or make new ones. 

To format the code please use the <a href="https://pypi.org/project/black/" target="_blank">black</a> and <a href="https://pypi.org/project/isort/" target="_blank">isort</a> packages. 

For the commits please follow the <a href="www.conventionalcommits.org" target="_blank">Conventional Commits Guideline</a>.

- Issue Tracker: https://github.com/gecad-group/peak-mas/issues
- Source Code: https://github.com/gecad-group/peak-mas/tree/main/src/peak

## License

`PEAK` is free and open-source, licensed under the <a href="https://github.com/gecad-group/peak-mas/blob/develop/LICENSE" target="_blank">GNU General Public License v3.0</a>.
