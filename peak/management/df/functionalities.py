import logging

from aioxmpp import JID
from aioxmpp.errors import XMPPCancelError

from peak.mas import CyclicBehaviour, Message, Template

from json import loads as json_loads

logger = logging.getLogger(__name__)

class PubSubCreateNode(CyclicBehaviour):

    async def on_start(self):
        logger.debug('starting PubSubCreateNode behaviour')
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
        self.logger = logging.getLogger(TreeHierarchy.__name__)
        self.logger.debug('starting behaviour')
        template = Template()
        template.set_metadata('resource', 'treehierarchy')
        self.set_template(template)
        self.agent.treehierarchy_data = {
            'nodes': set(),
            'links': set(),
            'categories': set(),
            'node_members': {}
        }

    async def run(self):
        msg = await self.receive(60)
        if msg:
            self.logger.debug('message received')
            path = msg.get_metadata('path')
            domain = msg.get_metadata('domain')
            nodes = path.split('/')
            self.logger.debug('nodes: ' + str(nodes))
            level = 'level'

            if msg.get_metadata('leave') and msg.sender in self.agent.treehierarchy_data['node_members'][nodes[-1]]:
                self.logger.debug(str(msg.sender) + ' leaving ' + path)
                self.agent.treehierarchy_data['node_members'][nodes[-1]].remove(msg.sender)
                nodes = nodes[::-1]
                #remove empty nodes and links
                for i, node in enumerate(nodes):
                    if len(self.agent.treehierarchy_data['node_members'][node]) == 0 and not any(node == source for source,_ in self.agent.treehierarchy_data['links']):
                        self.agent.treehierarchy_data['node_members'].pop(node)
                        self.agent.treehierarchy_data['nodes'].remove((node, level + str(len(nodes)-1-i), domain))
                        if i+1 < len(nodes):
                            self.agent.treehierarchy_data['links'].remove((nodes[i+1], node))
                existing_categories = set()

                #remove categories if empty
                for _, level, _ in self.agent.treehierarchy_data['nodes']:
                    existing_categories.add(level)
                difference = self.agent.treehierarchy_data['categories'].difference(existing_categories)
                if any(difference):
                    self.agent.treehierarchy_data['categories'] -= difference

            else:
                self.logger.debug(str(msg.sender) + ' entering ' + path)
                last = None
                for i, node in enumerate(nodes):
                    if node not in self.agent.treehierarchy_data['node_members']:
                        self.agent.treehierarchy_data['node_members'][node] = []
                    self.agent.treehierarchy_data['nodes'].add((node, level + str(i), domain))
                    self.agent.treehierarchy_data['categories'].add(level + str(i))
                    if last != None:
                        self.agent.treehierarchy_data['links'].add((last, node, max(len(self.agent.treehierarchy_data['node_members'][last])+1, len(self.agent.treehierarchy_data['node_members'][node]))))
                    last = node
                self.agent.treehierarchy_data['node_members'][last].append(msg.sender)

class CreateGraph(CyclicBehaviour):
    async def on_start(self):
        self.logger = logging.getLogger(CreateGraph.__name__)
        self.logger.debug('starting behaviour')
        template = Template()
        template.set_metadata('resource', 'graph')
        template.set_metadata('action', 'create')
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            self.logger.debug(msg.body)
            graph_name = msg.get_metadata('graph_name')
            graph_options = msg.get_metadata('graph_options')
            properties = json_loads(msg.get_metadata('properties'))
            self.agent.dataanalysis_data[graph_name] = {
                'graph_options': graph_options,
                'data': {}
            }
            for property in properties:
                self.agent.dataanalysis_data[graph_name]['data'][property] = []

class UpdateGraph(CyclicBehaviour):
    async def on_start(self) -> None:
        self.logger = logging.getLogger(UpdateGraph.__name__)
        self.logger.debug('starting behaviour')
        template = Template()
        template.set_metadata('resource', 'graph')
        template.set_metadata('action', 'update')
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            self.logger.debug(msg.body)
            graph_name = msg.get_metadata('graph_name')
            data = json_loads(msg.get_metadata('data'))
            for property in data:
                self.agent.dataanalysis_data[graph_name]['data'][property].append(data[property])
                self.logger.debug('updating property "' + property + '" : ' + str(data[property]))