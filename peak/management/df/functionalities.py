import logging

from aioxmpp import JID
from aioxmpp.errors import XMPPCancelError

from peak.mas import CyclicBehaviour, Message, Template


class PubSubCreateNode(CyclicBehaviour):  

    async def on_start(self):
        template = Template()
        template.set_metadata('resource', 'pubsub_create_node')
        self.set_template(template)          

    async def run(self):
        msg = await self.receive(60)
        if msg:
            affiliation = msg.get_metadata('affiliation')
            if not affiliation:
                affiliation = 'owner'
            node_jid = JID.fromstr(msg.get_metadata('node_jid'))
            pubsub = JID.fromstr(node_jid.domain)
            node = node_jid.localpart
            logger = logging.getLogger('PubSub')
            try:
                await self.agent.pubsub_client.create(pubsub, node)
            except XMPPCancelError:
                logger.debug('Node ' + str(node_jid) + ' already exists')
            aff = (str(msg.sender), affiliation)
            logger.debug('tuple: ' + str(aff))
            await self.change_node_affiliations(str(node_jid), aff)
            

            res = Message()
            res.to = str(msg.sender)
            res.set_metadata('resource', 'pubsub_create_node')
            await self.send(res)

class TreeHierarchy(CyclicBehaviour):

    async def on_start(self):
        template = Template()
        template.set_metadata('resource', 'treehierarchy')
        self.set_template(template)
        self.agent.graph = {
            'nodes': set(),
            'links': set(),
            'categories': set()
        }

    async def run(self):
        msg = await self.receive(60)
        if msg:
            path = msg.get_metadata('path')
            nodes = path.split('/')
            self.agent.graph['categories'].add({"name": nodes[0]})
            last = nodes[0]
            for node in nodes[1:]:
                self.agent.graph['links'].add({"source":last, "target":node})
                self.agent.graph['nodes'].add({"id":node, "name": node, "category":nodes[0]})
                last = node

            logger = logging.getLogger(__name__)
            logger.info('tree: ' + str(self.agent.nodes))


