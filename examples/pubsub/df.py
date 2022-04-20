from peak.mas import Agent, CyclicBehaviour, Template, Message
from aioxmpp import JID
from aioxmpp.errors import XMPPCancelError
import logging

class df(Agent):

    class PubSubCreateNode(CyclicBehaviour):            

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


    async def setup(self):
        template = Template()
        template.set_metadata('resource', 'pubsub_create_node')
        self.add_behaviour(self.PubSubCreateNode(), template)