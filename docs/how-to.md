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

<<<<<<< HEAD
So, what happened? Two agents were created. One called `john@localhost` and the other called `harry@localhost`. `john` sent a `Hello World` to `harry` and `harry` printed it out.

The way it works is simple. You can only define two root variables, the `defaults` and the `agents`. The `defaults` is used to define parameters to be applied to all agents. The `agents` variable defines the list of agents to be executed and their individual parameters. Type `peak start -h` on the terminal to see the list of available parameters. 

In this case we are defining, in the `defaults`, the default domain as `localhost` for all agents. In `agents` variable, we are defining two different types of agents, the `john` and the `harry`. In both agents we are defining their source file. The `agents` parameters will override the `defaults` parameters if they are the same.
=======
So, what happened? Two agents were created. One called `john@localhost` and the other called `harry@localhost`. `john` sent a message `Hello World` to `harry` and `harry` printed it out. The log file of `jonh` was in logging level `DEBUG`, and `harry`'s file was in level `INFO`.

The way it works is simple. You can only define two root variables, the `defaults` and the `agents`. The `defaults` is used to define parameters to be applied to all agents. The `agents` variable defines the list of agents to be executed and their respective parameters. The parameters available in `defaults` and in the agents of the variable `agents` can be seen using the `-h` argument in the `peak run` command. 

In this case we are defining, in the `defaults`, the default domain as `localhost` and the default logging level as `debug` for all agents. In `agents` variable, we are defining two different types of agents, the `john` and the `harry`. In `john` we are defining the agents source file. In `harry` we are defining the source file and the logging level, overriding the default value.
>>>>>>> main

There is the list of options that you can define in the configuration file, inside each agent and in the `defaults` variable:
- `file` - source file of the agent
- `domain` - domain of the server to be used for the agent's connection
- `resource` - resource to be used in the JID
- `log_level` - logging level of the log file
- `clones` - number of clones to be executed
<<<<<<< HEAD
=======
- `properties` - source file of the agent's properties (more on that later)
>>>>>>> main
- `verify_security` - if present verifies the SSL certificates

### Thread vs. Process
_In development_
This section will talk about how to run agents as different threads of the same process or as multiple processes and the benefits and use cases for each approach.

## PEAK Communities

<<<<<<< HEAD
In PEAK, communities can be seen as groups of agents that share similar goals. Communities are a very useful and efficient way to make communication between three or more agents. What makes this usefull is that for each message sent to the community every member will receive the message. 

<img src="peak_communities.png" height="300">

For this examples you will need to execute a pre-defined PEAK agent called Directory Facilitator, for short DF. He is responsable to maintain the PEAK communities structures. More details about the DF [here]().

### Creating a community ([Example 3](https://github.com/gecad-group/peak-mas/tree/main/examples/3_simple_community))

To create a community is very simple. There is a pre defined behavior that enables the agent join communities. For only this functionality you don't need DF, but it is recommended.
=======
The groups are a very useful way to make the communication between more than two agents. To create a group is very simple. There is a pre defined behavior that enables the agent to create and join groups. 
>>>>>>> main

```python
#agent.py
from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
<<<<<<< HEAD
        async def on_start(self):
            await self.wait_for(JoinCommunity("group1", f"conference.{self.agent.jid.domain}"))
=======
        async def on_start(self) -> None:
            await self.wait_for(JoinGroup("group1", f"conference.{self.agent.jid.domain}"))
>>>>>>> main

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

### Community tagging ([Example 4](https://github.com/gecad-group/peak-mas/tree/main/examples/4_community_tags))

Community tagging, as the name suggests, is for tagging communities. This allows the agents to identify the communities and then search for them using the tags to filter them. Let's see.

```python
#agent.py
from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour, SearchCommunity


class agent(Agent):
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
            def print_communities(tags, communities):
                print(f"Communities ({tags}): {communities}")

            await self.wait_for(SearchCommunity(["awesome"], print_communities))
            await self.wait_for(SearchCommunity(["test"], print_communities))
            
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

For this to work you need to execute the DF agent (more details [here]()). In the example above we create an agent that will create and tag two communities: `group1@conference.localhost` with tags `test` and `awesome`, and `group2@conference.localhost` with tag `test`. After that will search for communities using the `SearchCommunity` behavior. Note that for the `SearchCommunity` and for `LeaveCommunity` behaviours we do not add the behaviour directly to the agent, because the agent would stop before the behaviours would be accomplished. We use `wait_for` method, available in every behaviour, to wait for the completeness of the behaviour before continuing, making the behaviour synchrounous.

In simple words the tagging system will search for the communities that have the tags that you want. For instance, if you search for three tags it will give you every community that have all those three tags.

> **Chalenge 2:**
> Try to implement this example with two agents: one that creates and tags the communities and other that searches for them. ([Solution](https://github.com/gecad-group/peak-mas/tree/main/examples/chalenge_2))

### Community hierarchy ([Example 5](https://github.com/gecad-group/peak-mas/tree/main/examples/5_community_hierarchy))

The community hierarchy allows the user to create different levels of communities associated with one another. This does not only allow your agents to organize themselves but also to communicate more efficiently through the hierarchical branches. For instance, consider the hirarchy bellow.

_Image_

For every community of the hierarchy two nodes are created: the actual node of the community, which only the members can interact, and a node which has all the members of that community all the way down to the roots. This special node that we call the `echo node` will work has an echoer for the whole branch beneaf. In other words, if you want to send a message from X to Y you just need to send a message to the X_down node.

Let's see an example of the community hierarchy.

```python
#agent.py
# Standard library imports
from asyncio import sleep

# Reader imports
from peak import Agent, JoinCommunity, LeaveCommunity, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            groups_tree = [
                "peak/A0/B0",
                "peak/A0",
                "peak/A1",
                "peak/A2/B2/C0",
                "peak/A1/B3/C1",
            ]
            for groups_branch in groups_tree:
                await self.wait_for(
                    JoinCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)
            for groups_branch in groups_tree:
                await self.wait_for(
                    LeaveCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
```
For this to work you need to execute the DF agent (more details [here]()). In the `JoinCommunity` behavior you can specify a path representing the hierarchy of the communities. For instance in path `peak/A0/B0`, `peak` is the root community, beneath is community `A0`, at level 1, and `B0` at level 2. The last node of the path does not need necessarilly to be a leaf. We call the last node the target onde, because you only enter in that community specifically. 

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