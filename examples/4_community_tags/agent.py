# agent.py
# Reader imports
from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour, SearchCommunity


class agent(Agent):
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

            def print_communities(tags, communities):
                print(f"Communities ({tags}): {communities}")

            await self.wait_for(SearchCommunity(["awesome"], print_communities))
            await self.wait_for(SearchCommunity(["test"], print_communities))

            await self.wait_for(
                LeaveCommunity("group1", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveCommunity("group2", f"conference.{self.agent.jid.domain}")
            )
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.TagCommunities())
