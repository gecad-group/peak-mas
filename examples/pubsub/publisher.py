from peak.mas import Agent, OneShotBehaviour, Message, CreateNode
import logging
logger = logging.getLogger(__name__)

class publisher(Agent):

    class PublishItem(OneShotBehaviour):

        async def run(self):
            node = 'test@pubsub.localhost'
            create_node_behav = CreateNode(node)
            self.agent.add_behaviour(create_node_behav)
            await create_node_behav.join()
            msg = Message()
            msg.to = node
            msg.body = 'Ikie maluco'
            await self.publish(msg)
            logger.info('published')

    async def setup(self):
        self.add_behaviour(self.PublishItem())