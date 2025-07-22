FROM unclev/prosody-docker-extended

COPY prosody.cfg.lua /etc/prosody/prosody.cfg.lua

RUN mkdir -p /etc/prosody/certs

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/prosody/certs/localhost.key -out /etc/prosody/certs/localhost.crt -subj "/C=PT/ST=Porto/L=Porto/O=GECAD/CN=localhost"
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/prosody/certs/pubsub.localhost.key -out /etc/prosody/certs/pubsub.localhost.crt -subj "/C=PT/ST=Porto/L=Porto/O=GECAD/CN=pubsub.localhost"
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/prosody/certs/conference.localhost.key -out /etc/prosody/certs/conference.localhost.crt -subj "/C=PT/ST=Porto/L=Porto/O=GECAD/CN=conference.localhost"
