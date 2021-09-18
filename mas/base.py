import time
from typing import Callable, Iterable

import aioxmpp
import aioxmpp.callbacks
import spade
import spade.agent
import spade.behaviour
import spade.message


class _XMPPAgent(spade.agent.Agent):

    class MUCCreateService(spade.behaviour.OneShotBehaviour):

        async def run(self):
            if self.agent.muc_client == None:
                self.agent.muc_client = self.agent.client.summon(aioxmpp.MUCClient)

    class MUCJoin(spade.behaviour.OneShotBehaviour):

        def __init__(self, muc_jids: set[str]):
            super().__init__()
            self.muc_jids = muc_jids

        def on_muc_message_handler(self, msg, member, source, tracker=None, **kwargs):
            message = spade.message.Message().from_node(msg)
            sender = member.direct_jid
            self.agent.add_behaviour(self.agent.MUCOnMessageReceive(sender, message))

        def on_muc_failure_handler(self, exc):
            print(str(self.agent.jid) + ' - não entrei')
            raise exc

        async def run(self):
            for jid in self.muc_jids:
                room, _ = self.agent.muc_client.join(aioxmpp.JID.fromstr(jid), self.agent.jid.localpart)
                room.on_failure.connect(self.on_muc_failure_handler)
                room.on_message.connect(self.on_muc_message_handler)
                self.agent.rooms[jid] = room

    class MUCRequest(spade.behaviour.OneShotBehaviour):

        def __init__(self, muc_jid, msg: spade.message.Message, leave: bool):
            super().__init__()
            self.mud_jid = muc_jid
            self.msg = msg.prepare()
            self.leave = leave

        async def run(self):
            room, fut = self.agent.muc_client.join(aioxmpp.JID.fromstr(self.mud_jid), self.agent.jid.localpart)
            await fut
            await room.send_message(self.msg)
            if self.leave:
                await room.leave()

    class MUCOnMessageReceive(spade.behaviour.OneShotBehaviour):

        def __init__(self, sender, msg: spade.message.Message):
            super().__init__()
            self.sender = sender
            self.msg = msg

        async def run(self):
            print('pila ', self.msg.sender.resource)
            print('cona ', self.agent.jid.localpart)
            if self.msg.sender.resource != self.agent.jid.localpart:
                for template, handler in self.agent.message_handlers:
                    if template:
                        if  template.match(self.msg):
                            handler(self.sender, self.msg)
                    else:
                        handler(self.sender, self.msg)

    def __init__(self, jid,  password, muc_jids: set[str], verify_security = False):
        super().__init__(jid , password, verify_security)
        self.muc_client = None
        self.rooms = dict()
        self.message_handlers = list()
        self.add_behaviour(self.MUCCreateService())
        self.add_behaviour(self.MUCJoin(muc_jids))

    def send(self, msg: spade.message.Message, jid, *, leave=True) -> spade.behaviour.OneShotBehaviour:
        msg.sender = str(self.jid)
        b = self.MUCRequest(jid, msg, leave)
        self.add_behaviour(b)

    def room_members(self, jid) -> list:
        return self.rooms[jid].members

    '''
    handler must have two parameters: sender jid (string), message (spade message)
    '''
    def set_message_handler(self, handler: Callable, template: spade.template.Template = None):
        self.message_handlers.append(tuple((template, handler)))


class MASAgent(_XMPPAgent):

    class DFRegister(spade.behaviour.OneShotBehaviour):

        async def run(self):
            msg = spade.message.Message()
            msg.to = 'df@' + self.agent.jid.domain
            msg.set_metadata('register', 'agent')
            msg.set_metadata('types', self.setToString(self.agent.group_names))
            await self.send(msg)            

        def setToString(self, value):
            s = ''
            for v in value:
                s += v + ';'
            return s[:len(s)-1]
    
    def __init__(self, name, server, mas_name, group_names: set[str] = {}, verify_security = False):
        jid = name + '@' + server
        self.mas_name = mas_name
        self.group_names = group_names
        muc_jids , self.room_jids = self.create_muc_jids(group_names, server)
        super().__init__(jid, jid, muc_jids, verify_security)
        self.add_behaviour(self.DFRegister())

    def create_muc_jids(self, group_names, server):
        muc_jids = set()
        room_jids = dict()

        mas_muc_jid = self.mas_name + '@conference.' + server
        muc_jids.add(mas_muc_jid)
        room_jids[self.mas_name] = mas_muc_jid

        for name in group_names:
            jid = name + '-at-' + mas_muc_jid
            muc_jids.add(jid)
            room_jids[name] = jid

        return muc_jids, room_jids

    
    def send(self, msg: spade.message.Message, to = None, *, leave=False):
        '''Envia uma mensagem para um grupo
        '''
        jid = ''
        mas_muc_jid = self.mas_name + '@conference.' + self.jid.domain
        if to:
            jid = to + '-at-' + mas_muc_jid
        else:
            jid = mas_muc_jid
        super().send(msg, jid, leave=leave)

    def room_members(self, room) -> list:
        jid = self.room_jids[room] 
        return super().room_members(jid)


def run(*agents):

    for agent in agents:
        agent.start().result()

    def are_alive(agents):
        alive = False
        for agent in agents:
            alive = True if agent.is_alive() else alive
        return alive

    while are_alive(agents):
        try:
            time.sleep(10)
        except KeyboardInterrupt:
            break

