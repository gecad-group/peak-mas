from peak.mas import Agent, OneShotBehaviour,Message, JoinGroup
from asyncio import sleep

class agent(Agent):

    class HelloWorld(OneShotBehaviour):

        async def run(self):
            groups_tree = [
                'mas/retina2/teste',
                'mas/retina2',
                'mas/retina',
                'mas/test/test2/peak',
                'mas/retina/community/consumers'
            ]
            for groups_branch in groups_tree:
                await sleep(10)
                self.agent.add_behaviour(JoinGroup(groups_branch, 'conference.' + self.agent.jid.domain))
                group_leef = groups_branch.split('/')[-1]
                msg = Message(to=group_leef + '@conference.' + self.agent.jid.domain)
                msg.body = 'Hello World'
                await self.send_to_group(msg)


    async def setup(self):
        self.add_behaviour(self.HelloWorld())
