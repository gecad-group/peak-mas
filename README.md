# PEAK - Python-based framework for hEterogenous Agent Communities

![GitHub](https://img.shields.io/github/license/gecad-group/peak-mas)
![GitHub branch checks state](https://img.shields.io/github/checks-status/gecad-group/peak-mas/main)

PEAK is a multi-agent system framework which helps the users develop, monitor, analyse and maintain ecosystem of heterogeneous agent communities. This ecosystem is  where various multi-agent systems can coexist, interact and share resources between them. 
This framework is based on [SPADE](https://spade-mas.readthedocs.io/en/latest/). 

## Prerequisites

- Python >= 3.9.6
- XMPP Server (configurations, more on that later)


## Installing PEAK

- Conda
To install using conda, download the environment.yml file from the repository and then use the following command:
```bash
conda env create --file environment.yml	
```
This will create a conda environment called _peak_.

- Pip
To install using pip, just type the following command:
```bash
pip install peak
```


## Using PEAK

- Notes on SPADE
As already said PEAK is based on SPADE. This means that every functionality of SPADE is available to the user. We highly recommend you to see SPADE examples and documentation before starting using PEAK. Once you are familiarized with SPADE's mechanics you can start using PEAK.

- Notes on XMPP
To run any PEAK's agent you will need a XMPP server. To that you can either configure one on your machine, remotely or even use a public server. The only issue with the public servers is that some PEAK's functionalities will not work. To configure the server you can read the "Configure XMPP server" section in the documentation.

- Single Agent
One thing that was added in PEAK was the way the user executes the agents. PEAK added a CLI, inspired in JADE, to help the user execute end configure each agent in a easy and intuitive manner.
In this example we will show you how to execute a single agent. Save the following code in a file called `agent.py`.

```python 
from peak import Agent

from peak.behaviours import OneShotBehaviour

  
  

class agent(Agent):

    class HelloWorld(OneShotBehaviour):

        async def run(self) -> None:

            print("Hello World")

            await self.agent.stop()

  

    async def setup(self) -> None:

        self.add_behaviour(self.HelloWorld())
```
It is necessary that the name of the file is the same as the name of the agent's class so PEAK can do the proper parsing. This agent only has a behavior that prints to the terminal the "Hello World" message. To execute the agent just type the following command:
```bash 
peak path/to/agent.py -j agent@localhost
```
Change the `localhost` to the domain of the XMPP server you want to connect.
> [!note] 
> If you want to know more about each command we recommend reading the documentation or using the `-h` option to see the help message. 

- Multi-Agent

## Support

Use the Discussion tab in the repository if you have any question.
To alert a issue or a bug please post in the Issues tab.

## Roadmap

- Docker for XMPP server and peak environment
- Change config file from txt to YAML
- Add dynamic speed option to the internal clock

## Contributing to PEAK
- Use black and isort
- Follow the conventional commits guideline
- Create a branch of the develop branch and make a pull request to it

## Contact

## License

This project is under the GPLv3 license.
