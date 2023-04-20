# Standard library imports
from asyncio import sleep

# Reader imports
from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour


class tagger(Agent):
    class TagCommunities(OneShotBehaviour):
        async def run(self) -> None:
            self.agent.add_behaviour(
                JoinCommunity(
                    "group1",
                    f"conference.{self.agent.jid.domain}",
                    ["test", "awesome"],
                )
            )
            self.agent.add_behaviour(
                JoinCommunity("group2", f"conference.{self.agent.jid.domain}", ["test"])
            )
            await sleep(10)
            await self.wait_for(
                LeaveCommunity("group1", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveCommunity("group2", f"conference.{self.agent.jid.domain}")
            )
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.TagCommunities())
