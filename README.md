# PEAK - Python-based framework for heterogenous agent communities

![GitHub](https://img.shields.io/github/license/gecad-group/peak-mas) ![GitHub branch checks state](https://img.shields.io/github/checks-status/gecad-group/peak-mas/main)

PEAK is a multi-agent system framework which helps the users develop, monitor, analyze and maintain ecosystem of heterogeneous agent communities. This ecosystem is  where various multi-agent systems can coexist, interact and share resources between them. 
This framework is based on [SPADE](https://spade-mas.readthedocs.io/en/latest/). 

## Prerequisites

- Python == 3.9.6
- XMPP Server (configurations, more on that later)
- Linux or Windows (Mac not tested)


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

As already said PEAK is based on SPADE. This means that every functionality of SPADE is available to the user. We highly recommend you to see [SPADE](spade-mas.readthedocs.io) examples and documentation before starting using PEAK. Once you are familiarized with SPADE's mechanics you can start using PEAK.

### Notes on XMPP

To run any PEAK's agent you will need a XMPP server. You can either configure one on your machine, remotely or use a public server. The only issue with the public servers is that they don't usually have all the configurations required to run some PEAK's functionalities. To configure the server you can read the "Configure XMPP server" section in the [documentation](http://www.gecad.isep.ipp.pt/peak).

### Single Agent

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
$ peak run path/to/agent.py -j agent@localhost
```
Change the `localhost` to the domain of the XMPP server you want to connect.

<details><summary>Note</summary>
<p>

If you want to know more about each command we recommend reading the [documentation](http://www.gecad.isep.ipp.pt/peak) or using the `-h` option to see the help message.

</p>
</details>

For more advanced functionalities and examples we recommend you to head forward to the [documentation website](http://www.gecad.isep.ipp.pt/peak).


## Support

Use the [Discussion](https://github.com/gecad-group/peak-mas/discussions) page if you have any questions or ideas you would like so see implemented.
To alert an issue or a bug please post in the [Issues](https://github.com/gecad-group/peak-mas/issues) page.

## Roadmap

This are some functionalities that are being developed and will be released in a near future:
- [ ] Create a Docker for XMPP server and PEAK.
- [ ] Add dynamic speed option to PEAK's internal clock.
- [ ] Add multi-threading option to the execution configurations.
- [ ] Implement Yellow Page Service in DF agent.
- [ ] Implement Data Analysis section in the Dashboard.

## Contributing to PEAK

Pull requests are welcome. For major changes, please open a discussion first to discuss what you would like to change.

The examples are used as a form of testing the framework. So please make sure to update the examples as appropriate or make new ones. 

To format the code please use the [black](https://pypi.org/project/black/) and [isort](https://pypi.org/project/isort/) packages. 

For the commits please follow the [Conventional Commits Guideline](www.conventionalcommits.org).

## License

`PEAK` is free and open-source software licensed under the [GNU General Public License v3.0](https://github.com/gecad-group/peak-mas/blob/develop/LICENSE).
