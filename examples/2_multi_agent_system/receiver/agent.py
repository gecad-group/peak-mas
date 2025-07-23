from receiver.behaviors import ReceiveHelloWorld

from peak import Agent


class agent(Agent):
    async def setup(self):
        self.add_behaviour(ReceiveHelloWorld())
