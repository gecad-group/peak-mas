from queue import Queue
import aioxmpp as xmpp
from aioxmpp.stanza import Message

df = 'df@localhost'
messages = Queue()
jid = 'admin@localhost'

def message_received(msg):
    messages.put(msg)

client = xmpp.Client(jid, xmpp.make_security_layer(jid, no_verify=True)) 
message_dispatcher = client.summon(xmpp.dispatcher.SimpleMessageDispatcher)
message_dispatcher.register_callback(xmpp.MessageType.CHAT,None,message_received)
client.start()

async def send(message: Message):
    await client.send(message)

async def room_list():
    msg = Message()
    msg.set_metadata('resource', 'room_list')
    await client.send(msg)
    res = messages.get(timeout=60)
    return res.get_metadata('room_list').split(';')


