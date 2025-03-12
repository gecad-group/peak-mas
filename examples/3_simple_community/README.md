# Simple Community Agent Example

This example demonstrates how to create a simple agent that joins a community, sends a hello and goodbye message and then leaves the community using PEAK-MAS community capabilities.


## Explanation:


To create a community is very simple. There is a pre defined behavior that enables the agent join communities. For only this functionality you don’t need DF, but it is recommended.

As you can see in the example, the agent has a behavior HelloWorld. This behavior will first use the JoinCommunity behavior to join a community called group1@conference.localhost. If the community does not exists it will create it automatically. It waits until the agent joins the community. After that it will send a Hello World message to the community, waits for 5 seconds and then sends a Goodbye World and leaves the community with the LeaveCommunity behaviour.

> Note: For the this functionality to work the server must have Multi-User Chat functionality activated. You need to create a component in the server and give it a prefix, in this case is ‘conference’. See the [server configuration file example.](https://gecad-group.github.io/peak-mas/xmpp_config.html)

> Tip: You can see the messages being sent if you use the XMPP client and enter in the same room as the agent. Is a good way to debug the multi-agent.

> Chalenge 1: Try to implement the Communication between agents example using communities.

## How to run the code:

1. Ensure you have PEAK-MAS installed:

```bash
pip install peak-mas
```

2. Run the agent:

```bash
peak run -j agent@localhost agent.py
```

or 
    
```bash
peak start mas.yaml
```

## Expected output:

The agent will join the community, send the messages, and then leave. The actions will be logged in the log file in the logs folder.

## How can I use this in my project?

If you want to use this example as a base for your project, you can copy the `agent.py` file and the `mas.yaml` file to your project and modify the `agent.py` file to implement your own logic. 

You may have in consideration that the XMPP is designed to send system messages, so you may need to modify this code to use Templates to specify what kind of message you want to handle.

With PEAK-MAS, you can create complex agents that can interact with the environment and other agents in different ways. For more information about PEAK-MAS, check the documentation on the [PEAK-MAS website](https://gecad-group.github.io/peak-mas/).