from sender.behaviors import SendHelloWorld

from peak import Agent


class agent(Agent):
    async def setup(self):
        self.add_behaviour(SendHelloWorld())
