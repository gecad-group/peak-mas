from peak import Agent, OneShotBehaviour, getLogger

logger = getLogger(__name__)


class receiver(Agent):
    class ReceiveHelloWorld(OneShotBehaviour):
        async def run(self):
            logger.info("waiting for message")
            msg = await self.receive()
            logger.info(f"{msg.sender} sent me a message: '{msg.body}'")
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.ReceiveHelloWorld())
