# Docker for the XMPP server

This docker is only for the XMPP server and the Directory Facilitator agent. The only files missing are the certificates that must be in the folder `server/config/certs`.
To create self-assign certificates you can use OpenSSL to do it. The name of the certificates must be `localhost.key` and `localhost.crt`.