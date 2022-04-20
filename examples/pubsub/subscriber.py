from peak.mas import Agent, CyclicBehaviour
import time

class subscriber(Agent):

    class Test(CyclicBehaviour):

        async def run(self):
            msg = await self.receive(60)
            if msg:
                print(str(msg))

    async def setup(self):
        await self.subscribe('test@pubsub.localhost')
        self.add_behaviour(self.Test())