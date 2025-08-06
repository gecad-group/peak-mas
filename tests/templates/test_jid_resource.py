from peak import JID, Message, Template

template = Template()
template.sender = "sender1@host"
template.to = "recv1@host"
template.body = "Hello World"
template.thread = "thread-id"
template.metadata = {"performative": "query"}

message = Message()
message.sender = "sender1@host"
message.to = "recv1@host"
message.body = "Hello World"
message.thread = "thread-id"
message.set_metadata("performative", "query")

assert template.match(message)

template = Template()
template.sender = "sender1@host/main"

message = Message()
message.sender = "sender1@host"

assert not template.match(message)

template = Template()
template.sender = "sender1@host/main"

message = Message()
message.sender = "sender1@host/main"

assert template.match(message)

template = Template()
template.sender = "host"

message = Message()
message.sender = "sender1@host/maintest"

assert template.match(message)

message = Message()
message.sender = "sender1@host"

assert template.match(message)

template = Template()
template.set_metadata("host")

message = Message()
message.set_metadata("host", "192.168.1.1")

assert template.match(message)

template = Template()
template.set_metadata("host", "192.168.1.2")

message = Message()
message.set_metadata("host", "192.168.1.1")

assert not template.match(message)

template = Template()
template.set_metadata("host")

message = Message()
message.set_metadata("ip", "192.168.1.1")

assert not template.match(message)

template = Template()
template.to = JID.fromstr("recv1@host/main")
template.sender = JID.fromstr("sender1@host/main")

message = Message()
message.to = JID.fromstr("recv1@host/main")
message.sender = JID.fromstr("sender1@host")

assert not template.match(message)
