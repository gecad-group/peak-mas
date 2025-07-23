from peak import Message, Template

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
