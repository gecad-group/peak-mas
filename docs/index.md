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

That's easier than it can ever be!

## Table of Contents

- [Foreword](foreword.md)
- [Prerequisites](prerequistites.md)
- [Installing PEAK](installation.md)
- [How-to Guide](how-to.md)
	- [Run and configure a MAS](how-to.md#run-and-configure-a-mas)
	- [Create a simulation environment](how-to.md#create-simulation-environment)
	- [Integrate real smart devices](how-to.md#integrate-real-smart-devices)
	- [Integrate data providers](how-to.md#integrate-data-providers)
	- [PEAK Dashboard](how-to.md#peak-dashboard)
- [API Documentation](api-doc.md)
- [Contributing](contributing.md)
- [Contacts](contacts.md)

## Copyright Notice

`PEAK` is an open source project by [gecad-group](). See the original [LICENSE](https://github.com/gecad-group/peak-mas/blob/master/LICENSE) for more information.
