# How-to Guides

This section will give you some guidance regarding PEAK's functionalities.

## Run and configure a MAS
You have two options to run agents with PEAK. You can run the same way as the SPADE framework or using the command line interface (CLI). 

> **Note:**
> You can use the `-h` argument in `peak` comands and subcommands to know which arguments you can use.
> e.g. 
> ```bash
> $ peak -h
> usage: peak [-h] [-version] [-v] {df,run,start} ...                                                                                                                                                                                             positional arguments:                                                                                                     {df,run,start}                                                                                                            df            Execute Directory Facilitator agent.                                                                      run           Execute PEAK's agents.                                                                                    start         Executes multiple agents using a YAML configuration file.                                                                                                                                                                     optional arguments:                                                                                                       -h, --help      show this help message and exit                                                                         -version        show program's version number and exit                                                                  -v              Verbose. Turns on the debug info.
> ```

### Run a single agent

Let's run a simple agent.

```python
# agent.py
from peak import Agent, OneShotBehaviour
  
class agent(Agent):

    class HelloWorld(OneShotBehaviour):
        async def run(self) -> None:
            print("Hello World")
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.HelloWorld())
```

Consider the agent above. Create a file called agent.py and copy the code. This is a simple agent that will print "Hello World" in the terminal. 

To execute the agent you only need to open the directory of the agent.py in the CLI and then use the following command.

```bash
$ peak run agent.py -j dummy@localhost/test
```

> **Note:**
> The name of the agent file must be the same as the agent class. That is the only way for PEAK to know which objects to run when executing and agent.

In this comand we are telling PEAK to run the agent that is in the file `agent.py` with the JID `dummy@localhost/test`. 

The JID is the ID used in the XMPP protocol and is devided by three parts: the localpart, the domain and the resource (`localpart@domain/resource`). The localpart is required and is the username of the agent. The domain is also required and is the domain of the server you want the agent to log in. The resource is optional and is used to differentiate different sessions of the the same user. The resource, when missing, is created random internly. 

After you run the agent you will see a new folder appear in the same directory of the agent.py file. That folder is the `logs` folder and will contain the log files created for each agent you run. You can change the logging level for each agent using the command line argument `-l`. This files come preaty handy when running complex systems with lots of behaviours. You can track everything the agent and time when it does with this files.

### Run multiple agents

To run multiple agents, instead of just creating as many terminal sessions as agents, you can use a configuration file in YAML format.

```yaml
# dummies.yml
defaults:
	domain: localhost
	log_level: debug
agents:
	agent1:
		file: agent.py
		resource: test
	agent2: 
		file: agent.py
		clone: 2
```

Let's use the same agent.py file as the previous exercise. In the same directory create the YAML file above with the name `dummies.yml`. After that, run the following command:

```bash
$ peak start dummies.yml
```

Before diving into the YAML structure let me tell you what this command did. Three agents were created. One called `agent1@localhost/test`, other called `agent20@localhost` and the third one `agent21@localhost`. Each one of the agents printed `Hello World` in the terminal and the log files created were in loggin level `DEBUG`.




### Thread vs. Process
In development

## Create a group of agents
- MUC
- Group tagging
- Group Hierarchy

## Create a simulation environment
- Clock
- Dynamic clock

## Integrate real smart devices
- ModBus/TCP
- HTTPs
- Extending

## Integrate data providers
- Excel
- CSV

## PEAK Dashboard
- Group node graph
- Graph visualization
- Graph costumisation