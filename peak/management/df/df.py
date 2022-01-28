import aioxmpp as _aioxmpp
import spade
from spade.message import Message

import database


class DF(spade.agent.Agent):

    class ReceiveAgentID(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(60)
            if msg:
                jid = str(msg.sender.bare()) 
                self.agent.presence.subscribe(jid)
                player_types = msg.get_metadata('types')
                mas = msg.get_metadata('mas')
                database.Agent.add(jid, mas, player_types)

    class RoomList(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(60)
            if msg:
                sender = str(msg.sender.bare()) 
                new_msg = Message(sender, str(self.agent.jid))
                room_list = await self.agent.list_rooms()
                print('room: ', room_list)
                new_msg.set_metadata('resource', 'room_list')
                new_msg.set_metadata('room_list', room_list)
                await self.send(new_msg)

    class RoomMembers(spade.behaviour.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(60)
            if msg:
                sender = str(msg.sender.bare()) 
                new_msg = Message(sender, str(self.agent.jid))
                room = msg.get_metadata('room')
                members_list = await self.agent.list_members(room)
                new_msg.set_metadata('resource', 'room_members')
                new_msg.set_metadata('room', room)
                new_msg.set_metadata('room_members', members_list)
                await self.send(new_msg)

    def __init__(self, jid, password, verify_security=False):
        self.rooms = dict()
        self.disco = None
        super().__init__(jid, password, verify_security)

    async def _hook_plugin_after_connection(self):
        '''
        Executed after SPADE Agent's connection.

        This method adds the MUC service to the Agent XMPP Client and
        adds a message dispatcher for the group(MUC) messages.
        '''
        self.disco = self.client.summon(_aioxmpp.DiscoClient)

    async def list_rooms(self):
        info = await self.disco.query_items(_aioxmpp.JID.fromstr('conference.' + self.jid.domain), require_fresh=True)
        mas = ''
        print(len(info.items))
        for item in info.items:
            mas = mas + ';' + item.name
        return mas[1:]

    async def list_members(self, room):
        info = database.Agent.find_by_mas(room)
        members = ''
        for item in info:
            members = members + ';' + item.jid
        return members[1:]

    async def setup(self):
        template = spade.template.Template()
        template.set_metadata('register', 'agent')
        self.add_behaviour(self.ReceiveAgentID(), template)

        template = spade.template.Template()
        template.set_metadata('resource', 'room_list')
        self.add_behaviour(self.RoomList(), template)

        template = spade.template.Template()
        template.set_metadata('resource', 'room_members')
        self.add_behaviour(self.RoomMembers(), template)

