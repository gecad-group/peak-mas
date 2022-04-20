from peak.mas import Agent, OneShotBehaviour, Message, CreateNode

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

    async def setup(self):
        self.add_behaviour(self.PublishItem())