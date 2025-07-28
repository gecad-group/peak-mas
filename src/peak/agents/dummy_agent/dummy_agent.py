from peak import Agent, Message

from .behaviors import SendMessage


class DummyAgent(Agent):
    """Dummy agent for sending messages."""

    def __init__(self, message: Message, *args, **kargs):
        super().__init__(*args, **kargs)
        self.message = message

    async def setup(self):
        self.add_behaviour(SendMessage(self.message))
