# Standard library imports
from asyncio import sleep

# Reader imports
from peak import Agent, OneShotBehaviour, SearchCommunity


class searcher(Agent):
    class SearchForTags(OneShotBehaviour):
        async def run(self) -> None:
            await sleep(3)

            def print_groups(tags, groups):
                print(f"List of groups with tags {tags}: {str(groups)}")

            await self.wait_for(SearchCommunity(["test"], print_groups))
            await self.wait_for(SearchCommunity(["awesome"], print_groups))
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.SearchForTags())
