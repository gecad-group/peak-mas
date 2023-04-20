from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            groups_tree = [
                "peak/A0/B0",
                "peak/A0",
                "peak/A1",
                "peak/A2/B2/C0",
                "peak/A1/B3/C1",
            ]
            for groups_branch in groups_tree:
                await self.wait_for(
                    JoinCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)
            for groups_branch in groups_tree:
                await self.wait_for(
                    LeaveCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
