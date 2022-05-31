import aiohttp_cors

from aioxmpp import JID

from peak.mas import Agent
from peak.management.df.functionalities import TreeHierarchy, PubSubCreateNode

import logging

logger = logging.getLogger(__name__)

def df_name(domain):
    return 'df@' + domain + '/admin'

class DF(Agent):

    def __init__(self, domain, verify_security):
        super().__init__(JID.fromstr('df@' + domain + '/admin'), verify_security=verify_security)

    async def setup(self):
        self.graph = dict()

        self.add_behaviour(TreeHierarchy())
        self.add_behaviour(PubSubCreateNode())

        self.web.add_get("/tree", self.tree, template=None)

        # Configure default CORS settings.
        cors = aiohttp_cors.setup(self.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Configure CORS on all routes.
        for route in list(self.web.app.router.routes()):
            cors.add(route)

        # Start web API
        self.web.start(port=10000)

    async def tree(self, request):
        graph = {
            'nodes': list(self.graph['nodes']),
            'links': list(self.graph['links']),
            'categories': list(self.graph['categories']),
            'node_members': self.graph['node_members']
        }
        return graph

    async def tree_refresh(self, request):
        for node, _, domain in self.graph['nodes']:
            group_size = len(await self.group_members(node + '@' + domain))-1
            self.graph['node_members'][node] = group_size
        return self.graph













#class DF_old(Agent):
#
#    class ReceiveAgentID(CyclicBehaviour):
#
#        async def run(self):
#            msg = await self.receive(60)
#            if msg:
#                jid = str(msg.sender.bare()) 
#                self.agent.presence.subscribe(jid)
#                player_types = msg.get_metadata('types')
#                mas = msg.get_metadata('mas')
#                database.Agent.add(jid, mas, player_types)
#
#    class RoomList(CyclicBehaviour):
#
#        async def run(self):
#            msg = await self.receive(60)
#            if msg:
#                sender = str(msg.sender.bare()) 
#                new_msg = Message(sender, str(self.agent.jid))
#                room_list = await self.agent.list_rooms()
#                print('room: ', room_list)
#                new_msg.set_metadata('resource', 'room_list')
#                new_msg.set_metadata('room_list', room_list)
#                await self.send(new_msg)
#
#    class RoomMembers(CyclicBehaviour):
#
#        async def run(self):
#            msg = await self.receive(60)
#            if msg:
#                sender = str(msg.sender.bare()) 
#                new_msg = Message(sender, str(self.agent.jid))
#                room = msg.get_metadata('room')
#                members_list = await self.agent.list_members(room)
#                new_msg.set_metadata('resource', 'room_members')
#                new_msg.set_metadata('room', room)
#                new_msg.set_metadata('room_members', members_list)
#                await self.send(new_msg)
#
#    def __init__(self, jid, password, verify_security=False):
#        self.rooms = dict()
#        self.disco = None
#        super().__init__(jid, password, verify_security)
#
#    async def _hook_plugin_after_connection(self):
#        self.disco = self.client.summon(_aioxmpp.DiscoClient)
#
#    async def list_rooms(self):
#        info = await self.disco.query_items(_aioxmpp.JID.fromstr('conference.' + self.jid.domain), require_fresh=True)
#        mas = ''
#        print(len(info.items))
#        for item in info.items:
#            mas = mas + ';' + item.name
#        return mas[1:]
#
#    async def list_members(self, room):
#        info = database.Agent.find_by_mas(room)
#        members = ''
#        for item in info:
#            members = members + ';' + item.jid
#        return members[1:]
#
#    async def setup(self):
#        template = spade.template.Template()
#        template.set_metadata('register', 'agent')
#        self.add_behaviour(self.ReceiveAgentID(), template)
#
#        template = spade.template.Template()
#        template.set_metadata('resource', 'room_list')
#        self.add_behaviour(self.RoomList(), template)
#
#        template = spade.template.Template()
#        template.set_metadata('resource', 'room_members')
#        self.add_behaviour(self.RoomMembers(), template)
