from peak import Agent, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            print("Hello World")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
