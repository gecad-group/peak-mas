from peak.mas import Agent, OneShotBehaviour,Message, JoinGroup

class agent(Agent):

    class HelloWorld(OneShotBehaviour):

        async def run(self):
            msg = Message(to='peak@conference.'+self.agent.jid.domain)
            msg.body = 'Hello World'
            await self.send_to_group(msg)

    async def setup(self):
        self.add_behaviour(JoinGroup('mas/retina2', 'conference.localhost'))
        self.add_behaviour(JoinGroup('mas/retina', 'conference.localhost'))
        self.add_behaviour(JoinGroup('mas/test/test2/peak', 'conference.localhost'))
        self.add_behaviour(JoinGroup('mas/retina/community/consumers', 'conference.localhost'))
        self.add_behaviour(self.HelloWorld())
