# Standard library imports
from asyncio import sleep

# Reader imports
from peak import Agent, JoinGroup, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def on_start(self) -> None:
            behav = JoinGroup("group1", f"conference.{self.agent.jid.domain}")
            self.agent.add_behaviour(behav)
            await behav.join()

        async def run(self) -> None:
            msg = Message(to=f"group1@conference.{self.agent.jid.domain}")
            msg.body = "Hello World"
            await self.send_to_group(msg)
            await sleep(5)
            msg.body = "Goodbye World"
            await self.send_to_group(msg)
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.HelloWorld())
