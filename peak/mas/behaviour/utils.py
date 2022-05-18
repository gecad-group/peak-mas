import logging
from peak.mas import Template, Message, OneShotBehaviour
from peak.management.df.df import df_name


class CreateNode(OneShotBehaviour):

    def __init__(self, node: str, affiliation: str = None):
        super().__init__()
        self.affiliation = affiliation
        self.node = node
    
    async def on_start(self):
        self.template = Template()
        self.template.set_metadata('resource', 'pubsub_create_node')

    async def run(self):
        msg = Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata('resource', 'pubsub_create_node')
        msg.set_metadata('affiliation', self.affiliation if self.affiliation else '')
        msg.set_metadata('node_jid', self.node)
        await self.send(msg)
        res = await self.receive(60)
        if res:
            logger = logging.getLogger('CreateNode')
            logger.info('PubSub node ' + self.node + ' created')

class JoinGroup(OneShotBehaviour):

    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata('resource', 'treehierarchy')
        msg.set_metadata('path', self.path)
        await self.send(msg)
        nodes = self.path.split('/')
        for node in nodes[:-1]:
            await self.agent.join_group(node + '_down@' + self.domain)
        await self.agent.join_group(nodes[-1] + '@' + self.domain)
        await self.agent.join_group(nodes[-1] + '_down@' + self.domain)