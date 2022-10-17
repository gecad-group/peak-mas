# Prerequisites

To start using peak we will need a XMPP server. This serve is what will enable us to create the agents and make them communicate. XMPP is a protocol used for real time chatting so it's a good protocol for agents. You can either create and configure a local server or use a public one. The downside of using a public one is that some features of PEAK will not work (e.g. auto registration, multi-user chat, discovery service) depending on the server configuration. Another option is to use a docker, specially if you are on a Windows machine. We recommend the use of prosody XMPP server because it's more compatible. Another thing to be in mind is that the XMPP server and PEAK were only tested under Windows and Linux. 


## Run a XMPP server

To run and configure a local Prosody server you will need a Linux operating system. Prosody doesn't support Windows. If you have windows and want to install locally anyway you can either chose to run in a [Docker](#run-in-a-docker), using Windows Subsystem for Linux or using other [servers providers](https://xmpp.org/software/servers/). Bare in mind that PEAK is only tested in Prosody server, but feel free to post any question in the Discussion section at our repository.
To create a local server just go to [Prosody's docs](https://prosody.im/download/start). After creating the server head to [XMPP server configurations](#xmpp-server-configurations).

## Run in a Docker

There are some dockers available in Docker Hub. In the future we will make or own docker with the ability to run the server and the agents in the same docker. For now you can use [Prosody's official docker](https://github.com/prosody/prosody-docker). After creating the server head to [XMPP server configurations](#xmpp-server-configurations).

## XMPP server configurations

To be able to use every functionality in PEAK you need specific configurations on the server. Bellow is the configuration file that you can use to configure the server. Any additional configurations we can head to [Prosody's](https://prosody.im/doc/configure).

```lua
-- Prosody Example Configuration File

--

-- Information on configuring Prosody can be found on our

-- website at https://prosody.im/doc/configure

--

-- Tip: You can check that the syntax of this file is correct

-- when you have finished by running this command:

--     prosodyctl check config

-- If there are any errors, it will let you know what and where

-- they are, otherwise it will keep quiet.

--

-- The only thing left to do is rename this file to remove the .dist ending, and fill in the

-- blanks. Good luck, and happy Jabbering!

  
  

---------- Server-wide settings ----------

-- Settings in this section apply to the whole server and are the default settings

-- for any virtual hosts

  

-- This is a (by default, empty) list of accounts that are admins

-- for the server. Note that you must create the accounts separately

-- (see https://prosody.im/doc/creating_accounts for info)

-- Example: admins = { "user1@example.com", "user2@example.net" }

admins = {"df@localhost"}

  

-- Enable use of libevent for better performance under high load

-- For more information see: https://prosody.im/doc/libevent

--use_libevent = true

  

-- Prosody will always look in its source directory for modules, but

-- this option allows you to specify additional locations where Prosody

-- will look for modules first. For community modules, see https://modules.prosody.im/

-- For a local administrator it's common to place local modifications

-- under /usr/local/ hierarchy:

plugin_paths = {

    "/usr/local/lib/prosody/modules";

    "/home/happy_dori/Documentos/prosody-modules";

 }

  

-- This is the list of modules Prosody will load on startup.

-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.

-- Documentation for bundled modules can be found at: https://prosody.im/doc/modules

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

        "mam"; -- Store messages in an archive and allow users to access it

        "message_logging";

        --"csi_simple"; -- Simple Mobile optimizations

  

    -- Admin interfaces

        "admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands

        --"admin_telnet"; -- Opens telnet console interface on localhost port 5582

  

    -- HTTP modules

        --"bosh"; -- Enable BOSH clients, aka "Jabber over HTTP"

        --"websocket"; -- XMPP over WebSockets

        --"http_files"; -- Serve static files from a directory over HTTP

  

    -- Other specific functionality

        "posix"; -- POSIX functionality, sends server to background, enables syslog, etc.

        --"limits"; -- Enable bandwidth limiting for XMPP connections

        --"groups"; -- Shared roster support

        --"server_contact_info"; -- Publish contact information for this service

        --"announce"; -- Send announcement to all online users

        --"welcome"; -- Welcome users who register accounts

        --"watchregistrations"; -- Alert admins of registrations

        --"motd"; -- Send a message to users when they log in

        --"legacyauth"; -- Legacy authentication. Only used by some old clients and bots.

        --"proxy65"; -- Enables a file transfer proxy service which clients behind NAT can use

}

  

-- These modules are auto-loaded, but should you want

-- to disable them then uncomment them here:

modules_disabled = {

    -- "offline"; -- Store offline messages

    -- "c2s"; -- Handle client connections

    -- "s2s"; -- Handle server-to-server connections

}

  

-- Disable account creation by default, for security

-- For more information see https://prosody.im/doc/creating_accounts

allow_registration = true

-- Debian:

--   Do not send the server to background, either systemd or start-stop-daemon take care of that.

--

daemonize = false;

  

-- Debian:

--   Please, don't change this option since /run/prosody/

--   is one of the few directories Prosody is allowed to write to

--

pidfile = "/run/prosody/prosody.pid";

  

-- Force clients to use encrypted connections? This option will

-- prevent clients from authenticating unless they are using encryption.

  

c2s_require_encryption = true

  

-- Force servers to use encrypted connections? This option will

-- prevent servers from authenticating unless they are using encryption.

  

s2s_require_encryption = true

  

-- Force certificate authentication for server-to-server connections?

  

s2s_secure_auth = false

  

-- Some servers have invalid or self-signed certificates. You can list

-- remote domains here that will not be required to authenticate using

-- certificates. They will be authenticated using DNS instead, even

-- when s2s_secure_auth is enabled.

  

--s2s_insecure_domains = { "insecure.example" }

  

-- Even if you disable s2s_secure_auth, you can still require valid

-- certificates for some domains by specifying a list here.

  

--s2s_secure_domains = { "jabber.org" }

  

-- Select the authentication backend to use. The 'internal' providers

-- use Prosody's configured data storage to store the authentication data.

  

authentication = "internal_hashed"

  

-- Select the storage backend to use. By default Prosody uses flat files

-- in its configured data directory, but it also supports more backends

-- through modules. An "sql" backend is included by default, but requires

-- additional dependencies. See https://prosody.im/doc/storage for more info.

  

storage = "sql" -- Default is "internal" (Debian: "sql" requires one of the

-- lua-dbi-sqlite3, lua-dbi-mysql or lua-dbi-postgresql packages to work)

sql_manage_tables = true

message_logging_dir = "/var/log/prosody/message-log"

  

-- For the "sql" backend, you can uncomment *one* of the below to configure:

--sql = { driver = "SQLite3", database = "/home/happy_dori/Documentos/SQLite3/prosody.db" } -- Default. 'database' is the filename.

sql = { driver = "MySQL", database = "prosody", username = "root", password = "root", host = "localhost" }

--sql = { driver = "PostgreSQL", database = "prosody", username = "prosody", password = "secret", host = "localhost" }

  

network_backend = "epoll"

  

-- Archiving configuration

-- If mod_mam is enabled, Prosody will store a copy of every message. This

-- is used to synchronize conversations between multiple clients, even if

-- they are offline. This setting controls how long Prosody will keep

-- messages in the archive before removing them.

  

archive_expires_after = "never" -- Remove archived messages after 1 week

default_archive_policy = true

  

-- You can also configure messages to be stored in-memory only. For more

-- archiving options, see https://prosody.im/doc/modules/mod_mam

  

-- Logging configuration

-- For advanced logging see https://prosody.im/doc/logging

--

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

  

-- Uncomment to enable statistics

-- For more info see https://prosody.im/doc/statistics

-- statistics = "internal"

  

-- Certificates

-- Every virtual host and component needs a certificate so that clients and

-- servers can securely verify its identity. Prosody will automatically load

-- certificates/keys from the directory specified here.

-- For more information, including how to use 'prosodyctl' to auto-import certificates

-- (from e.g. Let's Encrypt) see https://prosody.im/doc/certificates

  

-- Location of directory to find certificates in (relative to main config file):

certificates = "certs"

  

-- HTTPS currently only supports a single certificate, specify it here:

--https_certificate = "/etc/prosody/certs/localhost.crt"

  

----------- Virtual hosts -----------

-- You need to add a VirtualHost entry for each domain you wish Prosody to serve.

-- Settings under each VirtualHost entry apply *only* to that host.

-- It's customary to maintain VirtualHost entries in separate config files

-- under /etc/prosody/conf.d/ directory. Examples of such config files can

-- be found in /etc/prosody/conf.avail/ directory.

  

------ Additional config files ------

-- For organizational purposes you may prefer to add VirtualHost and

-- Component definitions in their own config files. This line includes

-- all config files in /etc/prosody/conf.d/

  

VirtualHost "localhost"

  

--VirtualHost "example.com"

--  certificate = "/path/to/example.crt"

  

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

---Set up an external component (default component port is 5347)

--

-- External components allow adding various services, such as gateways/

-- transports to other networks like ICQ, MSN and Yahoo. For more info

-- see: https://prosody.im/doc/components#adding_an_external_component

--

--Component "gateway.example.com"

--  component_secret = "password"

Include "conf.d/*.cfg.lua"
```

## Debugging Tools

One way to debug PEAK, additionally to PEAK's debug system, is having a XMPP client to see the messages exchange between agents. There are plenty of [clients](https://xmpp.org/software/clients/) you can use. The one used to develop PEAK is [Pidgin](https://www.pidgin.im/).