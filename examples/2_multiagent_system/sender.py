from peak import Agent, Message, OneShotBehaviour


class sender(Agent):
    class SendHelloWorld(OneShotBehaviour):
        async def run(self):
            msg = Message(to="harry@localhost")
            msg.body = "Hello World"
            await self.send(msg)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.SendHelloWorld())
