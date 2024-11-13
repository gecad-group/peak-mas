# Community Hierarchy Example

This example demonstrates how to create an agent that interacts with a hierarchical community structure using PEAK-MAS community capabilities.

## Explanation

The community hierarchy allows the user to create different levels of communities associated with one another. This does not only allow your agents to organize themselves but also to communicate more efficiently through the hierarchical branches.

For every community of the hierarchy two nodes are created: the actual node of the community, which only the members can interact, and a node which has all the members of that community all the way down to the roots. This special node that we call the echo node will work has an echoer for the whole branch beneaf. In other words, if you want to send a message from X to Y you just need to send a message to the X_down node.

As can be seen in the example, the agent has a HelloWorld behaviour that involves interacting with multiple hierarchical communities. To do so it first joins multiple communities that are organised in a hierarchical structure. Once it has joined these communities, it sends a message to an echo node of those it belongs to, this echo node is used to be able to send a message to all agents within hierarchies and hierarchies below the community that is sent. This group is called with the suffix ‘a0_down’.

After sending the message, the agent waits for messages from the higher hierarchies. This is done by listening to the echo node of the community that is part of agent’s communities.

Finally, the agent leaves the communities it has joined and terminates.

## How to run the code

1. Ensure you have PEAK-MAS installed:

```bash
pip install peak-mas
```

2. Run the agent:

```bash
peak run -j agent@localhost agent.py
```

## Expected output

The agent will join the communities, send a message to a lower hierarchy, wait for messages from higher hierarchies, and then leave. All actions and received messages will be logged.

## How to use this in your project

You can use this example as a base for projects involving hierarchical agent communities. Copy the `agent.py` file to your project and modify it to implement your own logic.

Remember that XMPP is designed to send system messages as well as text messages. You may need to modify this code to use Templates to specify what kind of messages you want to handle.

For more information about PEAK-MAS and its capabilities, check the documentation on the [PEAK-MAS website](https://gecad-group.github.io/peak-mas/).