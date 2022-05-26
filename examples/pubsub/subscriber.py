from peak.mas import Agent, CyclicBehaviour
import time

class subscriber(Agent):

    class Test(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(60)
            if msg:
                print(str(msg))

        
    def on_item_published(self, jid, node, item, message=None):
        print(jid)
        print(node)
        print(item.__dict__.keys())
        print(message)

    async def setup(self):
        await self.subscribe('test@pubsub.localhost', self.on_item_published)
        self.add_behaviour(self.Test())