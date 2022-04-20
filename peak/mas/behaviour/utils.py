import logging
from peak.mas import Template, Message, OneShotBehaviour


class CreateNode(OneShotBehaviour):

    def __init__(self, node: str, affiliation: str = None):
        super().__init__()
        self.affiliation = affiliation
        self.node = node
        self.template = Template()
        self.template.set_metadata('resource', 'pubsub_create_node')

    async def run(self):
        msg = Message()
        msg.to = 'df@' + self.agent.jid.domain
        msg.set_metadata('resource', 'pubsub_create_node')
        msg.set_metadata('affiliation', self.affiliation if self.affiliation else '')
        msg.set_metadata('node_jid', self.node)
        await self.send(msg)
        res = await self.receive(60)
        if res:
            logger = logging.getLogger('CreateNode')
            logger.info('PubSub node ' + self.node + ' created')