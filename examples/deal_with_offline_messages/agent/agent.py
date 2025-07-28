from behaviors.message_server import MessageServer

from peak import Agent


class agent(Agent):
    async def setup(self):
        self.add_behaviour(MessageServer())
