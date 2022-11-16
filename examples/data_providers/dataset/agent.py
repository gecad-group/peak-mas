from peak import Agent, Message, PeriodicBehaviour


class agent(Agent):
    class PrintMessages(PeriodicBehaviour):
        async def on_start(self):
            self.count = 0

        async def run(self):
            msg = Message()
            msg.to = "peak@conference.localhost"
            msg.body = str(self.agent.message[self.count])
            await self.send_to_group(msg)

            if self.count == 5:
                await self.agent.stop()
            self.count += 1

    async def setup(self):
        await self.join_group("peak@conference.localhost")
        self.add_behaviour(self.PrintMessages(2))
