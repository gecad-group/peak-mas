# PEAK - Python-based framework for hEterogeneous Agent Communities

PEAK is a framework that helps users build, manage, analyze and maintain a multi-agent ecosystem. This ecosystem is where different multi-agent systems can coexist and share resources with it each other in a easy manner. 

PEAK is based on [SPADE](https://spade-mas.readthedocs.io/en/latest/) framework, which was built using the [XMPP](https://xmpp.org/) protocol. 

## PEAK made easy

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

You create an agent file like this one and then execute it using the following command:

```bash
$ peak agent.py -j agent@localhost
```

Thats easier than it can ever be!

## Table of Contents

- [Foreword]()
	- [SPADE and XMPP]()
- [Prerequisites]()
	- [Configuring a XMPP server]()
- [Installation](installation.md)
	- [Installing PEAK]()
- [How-to Guide](how-to.md)
	- [How to create a Simulation Environment?]()
		- [Clock]()
		- [Dynamic Clock]()
	- [How to integrate real smart devices into the MAS?]()
		- [Modbus/TCP]()
		- [HTTP]()
		- [Extending]()
	- [How to use data from data providers?]()
	- [How to use the PEAK Dashboard?]()
- [API Documentation](api-doc.md)
- [Contributing](contributing.md)
- [Contacts](contacts.md)

## Copyright Notice

`PEAK` is an open source project by [gecad-group](). See the original [LICENSE](https://github.com/gecad-group/peak-mas/blob/master/LICENSE) for more information.
