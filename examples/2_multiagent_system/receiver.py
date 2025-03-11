from peak import Agent, OneShotBehaviour, cli_logger


class receiver(Agent):
    class ReceiveHelloWorld(OneShotBehaviour):
        async def run(self):
            msg = await self.receive()
            cli_logger.info(f"{msg.sender} sent me a message: '{msg.body}'")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.ReceiveHelloWorld())
