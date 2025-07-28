from peak import Message, OneShotBehaviour, getLogger

logger = getLogger(__name__)


class SendMessage(OneShotBehaviour):
    """Sends a message to another agent."""

    def __init__(self, msg: Message):
        super().__init__()
        self.msg = msg

    async def run(self) -> None:
        await self.send(self.msg)
        logger.info(f"message sent: {self.msg}")
        await self.agent.stop()
