from peak import Agent, OneShotBehaviour


class receiver(Agent):
    class ReceiveHelloWorld(OneShotBehaviour):
        async def run(self):
            msg = await self.receive()
            print(f"{msg.sender} sent me a message: '{msg.body}'")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.ReceiveHelloWorld())
