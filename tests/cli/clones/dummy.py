from peak import Agent, OneShotBehaviour, debug


class dummy(Agent):
    class MyBehaviour(OneShotBehaviour):
        async def run(self):
            debug("Hello World!")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.MyBehaviour())
