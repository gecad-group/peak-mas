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
    "/usr/lib/prosody/modules-community";
}

-- This is the list of modules Prosody will load on startup.
-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.
modules_enabled = {
    -- Generally required
        "roster"; -- Allow users to have a roster. Recommended ;)
        "saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.
        "tls"; -- Add support for secure TLS on c2s/s2s connections
        --"dialback"; -- s2s dialback support
        "disco"; -- Service discovery

    -- Not essential, but recommended
        --"carbons"; -- Keep multiple clients in sync
        --"pep"; -- Enables users to publish their avatar, mood, activity, playing music and more
        "private"; -- Private XML storage (for room bookmarks, etc.)
        "blocklist"; -- Allow users to block communications with other users
        --"vcard4"; -- User profiles (stored in PEP)
        --"vcard_legacy"; -- Conversion between legacy vCard and PEP Avatar, vcard

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
-- Logs info and higher to /var/log
-- Logs errors to syslog also

log = {
    {levels = { min =  "info" }, to="console"};
    -- Log all error messages to prosody.err
    { levels = { min = "error" }, to = "file", filename = "/var/log/prosody/prosody.err" };
    -- Log everything of level "info" and higher (that is, all except "debug" messages)
    -- to prosody.log
    { levels = { min = "debug" }, to = "file", filename = "/var/log/prosody/prosody.log" };
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
