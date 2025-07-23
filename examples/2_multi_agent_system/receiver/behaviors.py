from peak import OneShotBehaviour, getLogger

logger = getLogger(__name__)


class ReceiveHelloWorld(OneShotBehaviour):
    async def run(self):
        logger.info("waiting for message")
        msg = await self.receive()
        logger.info(
            f"{msg.sender} sent me a message (thread: {msg.thread}): '{msg.body}'"
        )
        await self.agent.stop()
