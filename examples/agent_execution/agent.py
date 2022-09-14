from peak import Agent
from peak.behaviours import OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self) -> None:
            print("Hello World")
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.HelloWorld())
