# Reader imports
from peak import Agent, JoinGroup, Message, PeriodicBehaviour


class agent(Agent):
    class PrintMessages(PeriodicBehaviour):
        async def on_start(self):
            self.count = 0

        async def run(self):
            print(self.agent.message[self.count])

            if self.count == 5:
                await self.agent.stop()
            self.count += 1

    async def setup(self):
        self.add_behaviour(self.PrintMessages(2))
