# Prerequisites

To start using PEAK you will need a XMPP server. XMPP stands for Extensible Messaging and Presence Protocol. This server is what will enable us to create the agents and make them communicate. XMPP is a protocol used for real time chatting so it's a good protocol for agents. You can either create and configure a local server or use a public one. The downside of using a public one is that some features of PEAK will not work (e.g. auto registration, multi-user chat, discovery service) depending on the server configuration. Another option is to use a docker, specially if you are on a Windows machine. We recommend the use of Prosody XMPP server because it's more compatible. Another thing to be in mind is that the XMPP server and PEAK were only tested under Windows and Linux. 


## Run a XMPP server

To run and configure a local Prosody server you will need a Linux operating system. Prosody doesn't support Windows. If you have Windows and want to install locally anyway you can either chose to run in a [Docker](#run-in-a-docker), using Windows Subsystem for Linux or using other [servers providers](https://xmpp.org/software/servers/). Bare in mind that PEAK is only tested in Prosody server, but feel free to post any question in the Discussion section at our repository.
To create a local server just go to [Prosody's docs](https://prosody.im/download/start). After creating the server head to [XMPP server configurations](#xmpp-server-configurations).

## Run in a Docker

There are some dockers available in Docker Hub. In the future we will make or own docker with the ability to run the server and the agents in the same docker. For now you can use [Prosody's official docker](https://github.com/prosody/prosody-docker).

## XMPP server configurations

To be able to use every functionality in PEAK you need specific configurations on the server. Bellow is the configuration file that you can use to configure the server. This file only has the essentials to run PEAK features. For any additional configurations you can head to [Prosody's documentation](https://prosody.im/doc/configure).

> **Note:** 
> If you want to save messages logs in the server for debugging proposes use the `mam` and `message_logging` modules. Bare in mind that this will slow down your server, especially if you have high load on the server.


```lua
-- config.lua

-- Prosody Configuration File for PEAK
 
---------- Server-wide settings ----------

-- Settings in this section apply to the whole server and are the default settings
-- for any virtual hosts


-- This is the list of admins.
-- DF agent must be admin for some features to work.
admins = {"df@localhost"}

-- Enable use of libevent for better performance under high load
use_libevent = true

-- Paths for community models:
plugin_paths = {
    "/usr/local/lib/prosody/modules";
    "/home/happy_dori/Documentos/prosody-modules";
 }

-- This is the list of modules Prosody will load on startup.
-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.
modules_enabled = {
    -- Generally required
        "roster"; -- Allow users to have a roster. Recommended ;)
        "saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.
        "tls"; -- Add support for secure TLS on c2s/s2s connections
        "dialback"; -- s2s dialback support
        "disco"; -- Service discovery

    -- Not essential, but recommended
        "carbons"; -- Keep multiple clients in sync
        "pep"; -- Enables users to publish their avatar, mood, activity, playing music and more
        "private"; -- Private XML storage (for room bookmarks, etc.)
        "blocklist"; -- Allow users to block communications with other users
        "vcard4"; -- User profiles (stored in PEP)
        "vcard_legacy"; -- Conversion between legacy vCard and PEP Avatar, vcard

    -- Nice to have
        "version"; -- Replies to server version requests
        "uptime"; -- Report how long server has been running
        "time"; -- Let others know the time here on this server
        "ping"; -- Replies to XMPP pings with pongs
        "register"; -- Allow users to register on this server using a client and change passwords
        -- "mam"; -- Store messages in an archive and allow users to access it
        -- "message_logging"; -- Log/archive all user messages

    -- Admin interfaces
        "admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands  

    -- Other specific functionality
        "posix"; -- POSIX functionality, sends server to background, enables syslog, etc.
}

-- These modules are auto-loaded, but should you want
-- to disable them then uncomment them here:
modules_disabled = {
    "s2s"; -- Handle server-to-server connections
}

-- Allows agents to register freely
allow_registration = true

daemonize = false;
pidfile = "/run/prosody/prosody.pid";
c2s_require_encryption = true
network_backend = "epoll"
  
-- Select the authentication backend to use. The 'internal' providers
-- use Prosody's configured data storage to store the authentication data.
authentication = "internal_hashed"

-- Logging configuration
-- For advanced logging see https://prosody.im/doc/logging
-- Debian:
--  Logs info and higher to /var/log
--  Logs errors to syslog also

log = {
    -- Log files (change 'info' to 'debug' for debug logs):
    info = "/var/log/prosody/prosody.log";
    error = "/var/log/prosody/prosody.err";
    -- Syslog:
    { levels = { "error" }; to = "syslog";  };
}

certificates = "certs"


----------- Virtual hosts -----------

VirtualHost "localhost"

------ Components ------

-- You can specify components to add hosts that provide special services,
-- like multi-user conferences, and transports.
-- For more information on components, see https://prosody.im/doc/components

---Set up a MUC (multi-user chat) room server on conference.example.com:

Component "conference.localhost" "muc"
    muc_room_default_public = true
    muc_room_default_public_jids = true
    muc_room_locking = false
    max_history_messages = 0

Component "pubsub.localhost" "pubsub"
    autocreate_on_subscribe = true
    autocreate_on_publish = true

Include "conf.d/*.cfg.lua"
```

## XMPP Client (Optional)

One way to debug PEAK, additionally to PEAK's debug system, is having a XMPP client to see the messages exchange between agents. There are plenty of [clients](https://xmpp.org/software/clients/) you can use. The one used to develop PEAK is [Pidgin](https://www.pidgin.im/).