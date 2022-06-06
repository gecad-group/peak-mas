import logging

from aioxmpp import JID
from aioxmpp.errors import XMPPCancelError

from peak.mas import CyclicBehaviour, Message, Template

logger = logging.getLogger(__name__)

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
            'categories': set(),
            'node_members': {}
        }

    async def run(self):
        msg = await self.receive(60)
        if msg:
            path = msg.get_metadata('path')
            domain = msg.get_metadata('domain')
            nodes = path.split('/')
            logger.debug('nodes: ' + str(nodes))
            level = 'level'

            if msg.get_metadata('leave') and msg.sender in self.agent.graph['node_members'][nodes[-1]]:
                logger.debug('leave: true')
                self.agent.graph['node_members'][nodes[-1]].remove(msg.sender)
                nodes = nodes[::-1]
                #remove empty nodes and links
                for i, node in enumerate(nodes):
                    if len(self.agent.graph['node_members'][node]) == 0 and not any(node == source for source,_ in self.agent.graph['links']):
                        self.agent.graph['node_members'].pop(node)
                        self.agent.graph['nodes'].remove((node, level + str(len(nodes)-1-i), domain))
                        if i+1 < len(nodes):
                            self.agent.graph['links'].remove((nodes[i+1], node))
                existing_categories = set()

                #remove categories if empty
                for _, level, _ in self.agent.graph['nodes']:
                    existing_categories.add(level)
                difference = self.agent.graph['categories'].difference(existing_categories)
                if any(difference):
                    self.agent.graph['categories'] -= difference

            else:
                last = None
                for i, node in enumerate(nodes):
                    if node not in self.agent.graph['node_members']:
                        self.agent.graph['node_members'][node] = []
                    self.agent.graph['nodes'].add((node, level + str(i), domain))
                    self.agent.graph['categories'].add(level + str(i))
                    if last != None:
                        self.agent.graph['links'].add((last, node))
                    last = node
                self.agent.graph['node_members'][last].append(msg.sender)

                logger.debug('tree: ' + str(self.agent.graph))


