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
            logger = logging.getLogger(__name__)
            path = msg.get_metadata('path')
            nodes = path.split('/')
            logger.debug('nodes: ' + str(nodes))

            last = None
            level = 'level'
            for i, node in enumerate(nodes):
                self.agent.graph['nodes'].add((node, level + str(i)))
                self.agent.graph['categories'].add(level + str(i))
                if last != None:
                    self.agent.graph['links'].add((last, node))
                last = node

            logger.info('tree: ' + str(self.agent.graph))


