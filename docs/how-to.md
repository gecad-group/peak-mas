# How-to Guides

This section you will going through PEAK's functionalities. Every example given here is available in PEAK's repository.

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

To run multiple agents at the same time you can use a configuration file in YAML format.
```python
# sender.py
from peak import Agent, OneShotBehaviour, Message
  
class sender(Agent):

    class SendHelloWorld(OneShotBehaviour):
        async def run(self) -> None:
            msg = Message(to="harry@localhost")
            msg.body = "Hello World"
            await self.send(msg)
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.SendHelloWorld())
```

```python
# receiver.py
from peak import Agent, OneShotBehaviour
  
class receiver(Agent):

    class ReceiveHelloWorld(OneShotBehaviour):
        async def run(self) -> None:
	        while msg := await self.receive(10):
	            print(f"{msg.sender} sent me a message: '{msg.body}'")
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.ReceiveHelloWorld())
```

```yaml
# multiagent.yml
defaults:
	domain: localhost
	log_level: debug
agents:
	john:
		file: sender.py
		resource: test
		clones: 2
	harry: 
		file: receiver.py
		log_level: info
```

Let's create two agents one that sends the a message, the `receiver.py`, and one that receives the message, the `receiver.py`. In the same directory create the YAML file above with the name `multiagent.yml`. After that, run the following command:

```bash
$ peak start multiagent.yml
```

So, what happened? Three agents were created, instead of two. One called `john0@localhost/test`, other called `john1@localhost/test` and the third one `harry@localhost`. The two `john` sent a message `Hello World` to `harry` and `harry` print them out. The log files created were in loggin level `DEBUG`, except for the `harry` that was level `INFO`.

The strutucture of the configuration file is actually simple. You can only define two root variables, the `defaults` and the `agents`. The `defaults` is used to define parameters to be applied to all agents. The `agents` variable defines the list of agents to be executed and their respective parameters. 

In this case we are defining, in the `defualts`, the default domain as `localhost` and the default logging level as `debug` for all agents. In `agents` variable, we are defining two different types of agents, the `john` and the `harry`. In `john` we are defining the agents source file, the resource of the JID and how many clones we want from this type of agent. When clones are defined they use the exact same configuration, the only thing that changes is the name, adding the correspondent clone number after the agent name, in this case `john0` and `john1`. In `harry` we are defining the source file and the logging level, overriding the deafult value.

There is the list of options that you can define in the configuration file, inside each agent and in the deafults variable:
- file - source file of the agent
- domain - domain of the server to be used for the agent's connection
- resource - resource to be used in the JID
- log_level - loggin level of the log file
- clones - number of clones to be executed
- properties - source file of the agent's properties (more on that later)
- verify_security - if present verifies the SSL certificates

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