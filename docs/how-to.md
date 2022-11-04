# How-to Guides

In this section you will going through PEAK's functionalities. Every example given here is available in PEAK's repository.

## Run and configure a MAS

You have two options to run agents with PEAK. You can run the same way as in SPADE's doc or using the command line interface (CLI). 

> **Note:**
> You can use the `-h` argument in `peak` commands and subcommands to know which arguments you can use.
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

In this command we are telling PEAK to run the agent that is in the file `agent.py` with the JID `dummy@localhost/test`. 

The JID is the ID used in the XMPP protocol and is divided by three parts: the localpart, the domain and the resource (`localpart@domain/resource`). The localpart is required and is the username of the agent. The domain is also required and is the domain of the server you want the agent to log in. The resource is optional and is used to differentiate sessions of the the same user. The resource, when missing, is created randomly. 

After you run the agent you will see a new folder appear in the same directory of the agent.py file. That folder is the `logs` folder and will contain the log files created for each agent you run. You can change the logging level for each agent using the command line argument `-l`. This files come in handy when running complex systems with lots of behaviors. You can track everything the agent and time when it does with this files.

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

Let's create two agents one that sends the a message, the `sender.py`, and one that receives the message, the `receiver.py`. In the same directory create the YAML file above with the name `multiagent.yml`. After that, run the following command:

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
_In development_

## Create a group of agents

The groups are a very useful way to make the communication between agents. To create a group is very simple. There is a pre defined behavior that enables the agent to create and join groups. 

```python
#agent.py
from peak import Agent, JoinGroup, OneShotBehaviour, Message
from asyncio import sleep

class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def on_start(self) -> None:
            behav = JoinGroup("group1", f"conference.{self.agent.jid.domain}")
            self.agent.add_behaviour(behav)
            await behav.join()

        async def run(self) -> None:
            msg = Message(to=f"group1@conference.{self.agent.jid.domain}")
            msg.body = "Hello World"
            await self.send_to_group(msg)
            await sleep(5)
            msg.body = "Goodbye World"
            await self.send_to_group(msg)
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.HelloWorld())
```
As you can see in the example above, the agent has a behavior `HelloWorld`. This behavior will first use the `JoinGroup` behavior to join a group called 'group1@conference.localhost' (assuming the domain is ``localhost``). If the group does not exists it will create it. It waits until the agent joins the group. After that it will run the `run` function. The ``run`` function will send a `Hello World` message to the group, waits for 5 seconds and then sends a `Goodbye World` and exits. If you want to leave the group without terminating the agent you can import the ``LeaveGroup`` behavior from ``peak`` package and use it the same way as the `JoinGroup`.

> **Note:**
> For the this functionality to work the server must have Multi-User Chat functionality activated. You need to create a component in the server and give it a prefix, in this case is 'conference'. 

> **Tip:**
> You can see the messages being sent if you use the XMPP client and enter in the same room as the agent. Is a good way to debug the multi-agent.

### Group tagging

Group tagging, as the name suggests, is for tagging the groups. This allows the agents to identify the groups and then search for them using the tags to filter the groups. Let's see.

```python
#group_searcher.py
from peak import Agent, JoinGroup, SearchGroup
import logging
logger = logging.getLogger(self.__class__.__name__)

class group_searcher(Agent):
    async def setup(self) -> None:
        self.add_behaviour(
            JoinGroup("group1", "conference.localhost", ["test", "awesome", "cool"])
        )
        self.add_behaviour(
            JoinGroup("group2", "conference.localhost", ["test", "awesome"])
        )
        self.add_behaviour(
            JoinGroup("group3", "conference.localhost", ["test"],)
        )
        self.add_behaviour(JoinGroup("group4", "conference.localhost"))
        
        def print_groups(tags, groups):
            logger.info(str(tags), str(groups))
            
        self.add_behaviour(SearchGroup(["test"], print_groups))
        self.add_behaviour(SearchGroup(["awesome"], print_groups))
        self.add_behaviour(SearchGroup(["awesome", "cool"], print_groups))
```
In the example above we create an agent called `group_searcher`. This agent will create 4 different groups: `group1@conference.localhost` with the tags `test`, `awesome` and `cool`; `group2@conference.localhost` with the tags `test` and `awesome`; `group3@conference.localhost` with the tag `test`; and finally the fourth group `group4@conference.localhost`. After that will search for groups using the `SearchGroup` behavior.

Firstly, the `JoinGroup` is used to create the groups and tag them. The groups can have more than one tag. To search the groups it's used the `SearchGroup` behavior. You can search for more than one tag, but be careful because it used conjugation to search for them. In other words it will get you the list of groups that have all the tags the you mentioned.

### Group Hierarchy

The group hierarchy allows the user to create subgroups in different depths. This does not only allow you to organize your multiagent system (e.g., society of agent) but also to communicate more efficiently through the hierarchical branches. You can send a single message to every agent that is in a specific branch, or every agent bellow some specific node.

For this functionality you need to activate the Directory Facilitator (DF) agent. DF coordinates and monitors the hierarchical structure. To activate it you just need to run the following command:

```bash
$ peak df
```

To change the server domain use the `-d` argument.
Let's see an example of the group hierarchy.
```python
#agent.py
from asyncio import sleep
from peak import Agent, JoinGroup, LeaveGroup, Message, OneShotBehaviour

class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
			self.agent.add_behaviour(
				JoinGroup("mas/retina/teste", f"conference.{self.agent.jid.domain}")
			)
			msg = Message(
				to=f"retina@conference.{self.agent.jid.domain}"
			)
			msg.body = "Hello World"
			await self.send_to_group(msg)

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
```
In the JoinGroup behavior you can specify a path of groups. What these does is create an hierarchy of groups, being the first group the root and the last group an intermediate node or a leaf. In this path we call the last node the target group, because you only enter in that group specifically. Another interesting thing about this functionality is that for each node behind the target node you enter in a specially group which the names ends in \_down. The ideia behind this is to send messages to the whole branch, so every agent that enters a node bellow enters in this group. So if we want to send a message to the whole multi agent system we only have to send a message to, in the case of this example, ``mas_down``. In the example above the agent entered in 

> **Note:**
> In the Dashboard, the groups that end in \_down do not appear in the node graph.

## Create a simulation environment
### Clock
### Dynamic clock
_In development_

## Integrate data providers

Normally a multi-agent system uses external data so it can process that data. In PEAK you can integrate different data providers like files from the file system of your machine, databases in the web and from real devices using some real-time communication protocol.

### File System
- Excel
- CSV

### Smart devices
- ModBus/TCP
- HTTPs
- Extending

## PEAK Dashboard

The PEAK Dashboard is a separate project from PEAK. The Dashboard allows you to see in an interactive way the PEAK ecosystem using a web app. The Dashboard needs a Directory Facilitator (DF) agent in the XMPP server so it can monitor the system. The Dashboard communicates with the DF through its REST API. 
To know how to activate the DF run the following command:
```bash
$ peak df -h
```
### Ecosystem Insight
### Data Analysis
### Full Plot Customization