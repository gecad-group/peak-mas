from peak import Agent, JoinGroup, OneShotBehaviour, Message
from asyncio import sleep

class agent(Agent):

    class HelloWorld(OneShotBehaviour):
        async def run(self) -> None:
            await self.execute(JoinGroup("group1", f"conference.{self.agent.jid.domain}"))
            msg = Message(to=f"group1@conference.{self.agent.jid.domain}")
            msg.body = "Hello World"
            await self.send_to_group(msg)
            await sleep(5)
            msg.body = "Goodbye World"
            await self.send_to_group(msg)
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.HelloWorld())

