# PEAK: Python-based framework for heterogenous agent communities

[![DOI](https://img.shields.io/badge/DOI-10.1007%2F978--3--031--18050--7__7-blue)](https://link.springer.com/chapter/10.1007/978-3-031-18050-7_7)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/peak-mas)](https://pypi.org/project/peak-mas/)
[![PyPI](https://img.shields.io/pypi/v/peak-mas)](https://pypi.org/project/peak-mas/)
[![GitHub](https://img.shields.io/github/license/gecad-group/peak-mas)](https://github.com/gecad-group/peak-mas)
[![powered by](https://img.shields.io/static/v1?label=powered%20by&message=GECAD&color=177985&labelColor=de5d4a)](https://www.gecad.isep.ipp.pt/GECAD/Pages/Presentation/Home.aspx)
[![code style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)
[![imports isort](https://img.shields.io/static/v1?label=imports&message=isort&color=blue&labelColor=orange)](https://pycqa.github.io/isort/)

PEAK is a multi-agent system framework which helps the users develop, monitor, analyze and maintain ecosystem of heterogeneous agent communities. This ecosystem is  where various multi-agent systems can coexist, interact and share resources between them. 
This framework is based on <a href="https://spade-mas.readthedocs.io/en/latest/" target="_blank">SPADE</a>.


## Prerequisites

- Python == 3.9.6
- XMPP Server ([see docs](https://www.gecad.isep.ipp.pt/peak))


## Installing PEAK

### Conda

To install using conda, download the environment.yml file from the repository and then use the following command:
```bash
$ conda env create --file environment.yml	
```
This will create a conda environment called _peak_.

### Pip

To install using pip, just type the following command:
```bash
$ pip install peak-mas
```


## Using PEAK

### Notes on SPADE

As already said PEAK is based on SPADE. This means that every functionality of SPADE is available to the user. We highly recommend you to see <a href="https://spade-mas.readthedocs.io/en/latest/" target="_blank">SPADE</a> examples and documentation before starting using PEAK. Once you are familiarized with SPADE's mechanics you can start using PEAK.
For now PEAK is not compatible with version above 3.2.2 of SPADE.

### Notes on XMPP

To run any PEAK's agent you will need a XMPP server. You can either configure one on your machine, remotely or use a public server. The only issue with the public servers is that they don't usually have all the configurations required to run some PEAK's functionalities. To configure the server you can read the "Configure XMPP server" section in the <a href="http://www.gecad.isep.ipp.pt/peak" target="_blank">documentation</a>.

#### Using docker

To make it easier to configure the XMPP server we have created a docker image with the server already configured. To use it just type the following command in the /docker folder:

```bash
$ docker-compose up -d
```

### Hello World Agent Example

One thing that was added in PEAK was the way the user executes the agents. PEAK added a CLI, inspired in JADE, to help the user execute end configure each agent in a easy and intuitive manner.
In this example we will show you how to execute a single agent. Save the following code in a file called `agent.py`.

```python 
from peak import Agent, OneShotBehaviour

class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            print("Hello World")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
```
It is necessary that the name of the file is the same as the name of the agent's class so PEAK can do the proper parsing. This agent only has a behavior that prints to the terminal the "Hello World" message. To execute the agent just type the following command:
```bash 
$ peak run path/to/agent.py -j agent@localhost
```
Change the `localhost` to the domain of the XMPP server you want to connect.

<details><summary>Note</summary>
<p>

If you want to know more about each command we recommend reading the [documentation](http://www.gecad.isep.ipp.pt/peak) or using the `-h` option to see the help message.

</p>
</details>

For more advanced functionalities and examples we recommend you to head forward to the <a href="http://www.gecad.isep.ipp.pt/peak" target="_blank">documentation website</a>.


## Support

Use the <a href="https://github.com/gecad-group/peak-mas/discussions" target="_blank">Discussion</a> page if you have any questions or ideas you would like so see implemented.
To alert an issue or a bug please post in the <a href="https://github.com/gecad-group/peak-mas/issues" target="_blank">Issues</a> page.

## Roadmap

This are some functionalities that are being developed and will be released in a near future:
- [ ] Integrate FIPA ACL messages in PEAK.
- [ ] Add dynamic speed option to PEAK's internal clock.
- [ ] Add multi-threading option to the Command Line Interface.
- [ ] Implement Yellow Page Service in the Directory Facilitator agent.
- [ ] Implement physical mobility in the agents.

## Scientific Publications

- Ribeiro, B., Pereira, H., Gomes, L., Vale, Z. (2023). Python-Based Ecosystem for Agent Communities Simulation. In: , et al. 17th International Conference on Soft Computing Models in Industrial and Environmental Applications (SOCO 2022). SOCO 2022. Lecture Notes in Networks and Systems, vol 531. Springer, Cham. https://doi.org/10.1007/978-3-031-18050-7_7
- Pereira H, Ribeiro B, Gomes L, Vale Z. Smart Grid Ecosystem Modeling Using a Novel Framework for Heterogenous Agent Communities. Sustainability. 2022; 14(23):15983. https://doi.org/10.3390/su142315983
- Silva C, Faria P, Ribeiro B, Gomes L, Vale Z. Demand Response Contextual Remuneration of Prosumers with Distributed Storage. Sensors. 2022; 22(22):8877. https://doi.org/10.3390/s22228877


## Contributing to PEAK

Pull requests are welcome. For major changes, please open a discussion first to discuss what you would like to change.

The examples are used as a form of testing the framework. So please make sure to update the examples as appropriate or make new ones. 

To format the code please use the <a href="https://pypi.org/project/black/" target="_blank">black</a> and <a href="https://pypi.org/project/isort/" target="_blank">isort</a> packages. 

For the commits please follow the <a href="www.conventionalcommits.org" target="_blank">Conventional Commits Guideline</a>.

## License

`PEAK` is free and open-source software licensed under the <a href="https://github.com/gecad-group/peak-mas/blob/develop/LICENSE" target="_blank">GNU General Public License v3.0</a>.
