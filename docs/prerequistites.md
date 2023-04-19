# Prerequisites
To start using PEAK you will need a XMPP server. XMPP stands for Extensible Messaging and Presence Protocol. This server is what will enable us to create the agents and make them communicate. XMPP is a protocol used for real time chatting so it's a good protocol for agents. You can either create and configure a local server or use a public one. The downside of using a public one is that some features of PEAK will not work (e.g. auto registration, multi-user chat, discovery service) depending on the server configuration. Another option is to use a docker, specially if you are on a Windows machine. We recommend the use of Prosody XMPP server because it's more compatible. PEAK was tested under Windows and Linux. To use PEAK you can either run in a local XMPP server configured by you, or run in a Docker with the XMPP server inside. 


## Run in a XMPP server
To run and configure a local Prosody server you will need a Linux operating system. To create a local server just go to [Prosody's docs](https://prosody.im/download/start) and follow the instructions. After creating the server head to [XMPP server configurations](#xmpp-server-configurations). 
Prosody doesn't support Windows natively. If you have Windows and want to install locally you can either chose to run in a [Docker (see next section)](#run-in-a-docker), use Windows Subsystem for Linux (WSL) or use other [server providers](https://xmpp.org/software/servers/). Other servers providers may not be compatible with PEAK, but feel free to post in the [discussion forum](https://github.com/gecad-group/peak-mas/discussions) any problem you might find. 


## Run in a Docker
There are some dockers available in Docker Hub. In the future we will make or own docker with the ability to run the server and the agents in the same docker. For now you can use [Prosody's official docker](https://github.com/prosody/prosody-docker).

## XMPP server configurations
To be able to use every functionality in PEAK you need specific configurations on the server. Bellow is the configuration file that you can use to configure the server. This file only has the essentials to run PEAK features. For any additional configurations you can head to [Prosody's documentation](https://prosody.im/doc/configure).

If you are using other server than Prosody and want to know which functionalities you have to enable se the following list (its probable that you can not tweak or find every option in other servers):
- Allow users to register freely
- Multi-User Chat:
    - make the room public as default
    - make the JID's of the rooms public by default
    - de-enable room locking
    - change the max history messages to zero

See the example configuration file [here](xmpp_config.md).

> **Note:** 
> If you want to save messages logs in the server for debugging proposes use the `mam` and `message_logging` modules. Bare in mind that this will slow down your server, especially if you have high load on the server.


## XMPP Client

This is optional, but one good way to debug PEAK, additionally to PEAK's debug system, is having a XMPP client to see the messages exchange between agents. There are plenty of [clients](https://xmpp.org/software/clients/) you can use. The one used to develop PEAK is [Pidgin](https://www.pidgin.im/).