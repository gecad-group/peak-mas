# How-to Guides
This section will going to guide you through PEAK's fundamental ideas and functionalities. Every example given here is available in the [repository](https://github.com/gecad-group/peak-mas).

## PEAK Basic principles
You have two options to run PEAK agents. You can run the same way as in SPADE by using a python script or using PEAK's command line interface (CLI). 

> **Note:**
> After installing `peak` you can use the command `-h` to show you the commands available to you.
> e.g. 
> ```bash
> $ peak -h
> usage: peak [-h] [-version] [-v] {df,run,start} ...
>
> positional arguments:
>  {df,run,start}
>    df            Execute Directory Facilitator agent.
>    run           Execute PEAK agents.
>    start         Executes multiple agents using a YAML configuration
>                  file.
>
>optional arguments:
>  -h, --help      show this help message and exit
>  --version        show programs version number and exit
> ```

### How to create and Agent ([Example 1](https://github.com/gecad-group/peak-mas/tree/main/examples/1_simple_agent))
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

Consider the agent above. Create a file called `agent.py` and copy the code. This is a simple agent that will print "Hello World" in the terminal. 

To execute the agent you only need to open the directory where the file `agent.py` is in the CLI and then use the following command.

```bash
$ peak run agent.py -j dummy@localhost
```

> **Note:**
> The name of the file must be the same as the name of the class. That is the only way for PEAK to know which objects to run when executing an agent.

In this command we are telling PEAK to run the agent that is in the file `agent.py` with the JID `dummy@localhost`. 

The JID is the ID used in the XMPP protocol and is divided by three parts: the localpart, the domain and the resource (`localpart@domain/resource`). The localpart is required and is the username of the agent. The domain is also required and is the domain of the server you want the agent to log in. The resource is optional and is used to differentiate sessions of the the same user. The resource, when empty, is created randomly. 

After you run the agent you will see a new folder appear in the same directory of the `agent.py`. That folder is the `logs` folder and will contain the log files created for each agent you run. You can change the logging level for each agent using the command line argument `-l`. This files come in handy when running complex systems with lots of behaviors. You can track everything the agent does and when it does with the logging functionality.

### Communication between Agents ([Example 2](https://github.com/gecad-group/peak-mas/tree/main/examples/2_multiagent_system))

To run multiple agents at the same time you can use a configuration file in YAML format.
```python
# sender.py
from peak import Agent, OneShotBehaviour, Message
  
class sender(Agent):
    class SendHelloWorld(OneShotBehaviour):
        async def run(self):
            msg = Message(to="harry@localhost")
            msg.body = "Hello World"
            await self.send(msg)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.SendHelloWorld())
```

```python
# receiver.py
from peak import Agent, OneShotBehaviour
  
class receiver(Agent):
    class ReceiveHelloWorld(OneShotBehaviour):
        async def run(self):
            while msg := await self.receive(10):
                print(f"{msg.sender} sent me a message: '{msg.body}'")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.ReceiveHelloWorld())
```

```yaml
# mas.yaml
defaults:
    domain: localhost
agents:
    john:
        file: sender.py
    harry: 
        file: receiver.py
```

Let's create two agents one that sends the a message, the `sender.py`, and one that receives the message, the `receiver.py`. In the same directory create the YAML file above with the name `mas.yaml`. After that, run the following command:

```bash
$ peak start mas.yaml
```

So, what happened? Two agents were created. One called `john@localhost` and the other called `harry@localhost`. `john` sent a `Hello World` to `harry` and `harry` printed it out.

The way it works is simple. You can only define two root variables, the `defaults` and the `agents`. The `defaults` is used to define parameters to be applied to all agents. The `agents` variable defines the list of agents to be executed and their individual parameters. Type `peak start -h` on the terminal to see the list of available parameters. 

In this case we are defining, in the `defaults`, the default domain as `localhost` for all agents. In `agents` variable, we are defining two different types of agents, the `john` and the `harry`. In both agents we are defining their source file. The `agents` parameters will override the `defaults` parameters if they are the same.

There is the list of options that you can define in the configuration file, inside each agent and in the `defaults` variable:
- `file` - source file of the agent
- `domain` - domain of the server to be used for the agent's connection
- `resource` - resource to be used in the JID
- `log_level` - logging level of the log file
- `clones` - number of clones to be executed
- `verify_security` - if present verifies the SSL certificates

### Thread vs. Process
_In development_
This section will talk about how to run agents as different threads of the same process or as multiple processes and the benefits and use cases for each approach.

## PEAK Communities

In PEAK, communities can be seen as groups of agents that share similar goals. Communities are a very useful and efficient way to make communication between three or more agents. What makes this usefull is that for each message sent to the community every member will receive the message.

<img src="peak_communities.png" height="300">

### Creating a community ([Example 3](https://github.com/gecad-group/peak-mas/tree/main/examples/3_simple_community))

To create a community is very simple. There is a pre defined behavior that enables the agent join communities. 

```python
#agent.py
from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def on_start(self):
            await self.wait_for(JoinCommunity("group1", f"conference.{self.agent.jid.domain}"))

        async def run(self):
            msg = Message(to=f"group1@conference.{self.agent.jid.domain}")
            msg.body = "Hello World"
            await self.send_to_community(msg)
            await sleep(5)
            msg.body = "Goodbye World"
            await self.send_to_community(msg)
            self.kill()
        
        async def on_end(self):
            await self.wait_for(LeaveCommunity("group1", f"conference.{self.agent.jid.domain}"))
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
```
Then run the following command:
```bash
$ peak run agent.py -j dummy@localhost
```
As you can see in the example above, the agent has a behavior `HelloWorld`. This behavior will first use the `JoinCommunity` behavior to join a community called `group1@conference.localhost`. If the community does not exists it will create it automatically. It waits until the agent joins the community. After that it will send a `Hello World` message to the community, waits for 5 seconds and then sends a `Goodbye World` and leaves the community with the `LeaveCommunity` behaviour.

> **Note:**
> For the this functionality to work the server must have Multi-User Chat functionality activated. You need to create a component in the server and give it a prefix, in this case is 'conference'. See [this](xmpp_config.md) server configuration file example. 

> **Tip:**
> You can see the messages being sent if you use the XMPP client and enter in the same room as the agent. Is a good way to debug the multi-agent.

> **Chalenge 1:**
> Try to implement the [Communication between agents](#communication-between-agents-example-2) example using communities. ([Solution]())

### Community tagging ([Example 4](https://github.com/gecad-group/peak-mas/tree/main/examples/3_community_tagging))

Community tagging, as the name suggests, is for tagging communities. This allows the agents to identify the communities and then search for them using the tags to filter them. Let's see.

```python
#tagger.py
from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour


class tagger(Agent):
    class TagCommunities(OneShotBehaviour):
        async def run(self) -> None:
            self.agent.add_behaviour(
                JoinCommunity(
                    "group1",
                    f"conference.{self.agent.jid.domain}",
                    ["test", "awesome"],
                )
            )
            self.agent.add_behaviour(
                JoinCommunity(
                    "group2", f"conference.{self.agent.jid.domain}", ["test"]
                )
            )
            await sleep(10)
            await self.wait_for(
                LeaveCommunity("group1", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveCommunity("group2", f"conference.{self.agent.jid.domain}")
            )
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.TagCommunities())
```

In the example above we create an agent called `tagger` and `searcher`. `tagger` will create and tag two groups: `group1@conference.localhost` with the tags `test`, `awesome` and `cool`; `group2@conference.localhost` with the tags `test` and `awesome`; `group3@conference.localhost` with the tag `test`; and finally the fourth group `group4@conference.localhost`. After that will search for groups using the `SearchGroup` behavior.

Firstly, the `JoinGroup` is used to create the groups and tag them. The groups can have more than one tag. To search the groups it's used the `SearchGroup` behavior. You can search for more than one tag, but be careful because it used conjugation to search for them. In other words it will get you the list of groups that have all the tags the you mentioned.

> **Chalenge 2:**
> Try to implement this example with two agents: one that creates and tags the groups and other that searches for them. ([Solution](https://github.com/gecad-group/peak-mas/tree/main/examples/chalenge_2))

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

## Simulation Environment
### Clock
### Dynamic clock
_In development_

## PEAK Dashboard
The PEAK Dashboard is a separate project from PEAK. The Dashboard allows you to see in an interactive way the PEAK ecosystem using a web app. The Dashboard needs a Directory Facilitator (DF) agent in the XMPP server so it can monitor the system. The Dashboard communicates with the DF through its REST API. 
To know how to activate the DF run the following command:
```bash
$ peak df -h
```
### Ecosystem Overview
### Data Analysis
### Full Plot Customization