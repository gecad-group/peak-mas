from peak.mas import Agent, OneShotBehaviour,Message

class agent(Agent):

    class HelloWorld(OneShotBehaviour):

        async def run(self):
            msg = Message(to='peak@conference.'+self.agent.jid.domain)
            msg.body = 'Hello World'
            await self.send_to_group(msg)

    async def setup(self):
        await self.join_group('peak@conference.'+self.jid.domain)
        self.add_behaviour(self.HelloWorld())
