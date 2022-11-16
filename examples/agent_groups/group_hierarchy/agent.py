from asyncio import sleep

from peak import Agent, JoinGroup, LeaveGroup, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            groups_tree = [
                "mas/retina2/teste",
                "mas/retina2",
                "mas/retina",
                "mas/test/test2/peak",
                "mas/retina/community/consumers",
            ]
            for _ in range(3):
                for groups_branch in groups_tree:
                    await sleep(5)
                    self.agent.add_behaviour(
                        JoinGroup(groups_branch, "conference." + self.agent.jid.domain)
                    )
                    group_leef = groups_branch.split("/")[-1]
                    msg = Message(
                        to=group_leef + "@conference." + self.agent.jid.domain
                    )
                    msg.body = "Hello World"
                    await self.send_to_group(msg)
                for groups_branch in groups_tree:
                    await sleep(5)
                    self.agent.add_behaviour(
                        LeaveGroup(groups_branch, "conference." + self.agent.jid.domain)
                    )
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
