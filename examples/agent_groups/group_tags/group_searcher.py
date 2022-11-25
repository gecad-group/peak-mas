# Standard library imports
import logging
from asyncio import sleep

# Reader imports
from peak import Agent, OneShotBehaviour, SearchGroup


class group_searcher(Agent):
    class SearchGroups(OneShotBehaviour):
        async def run(self) -> None:
            await sleep(3)

            def print_groups(tags, groups):
                logging.getLogger(self.__class__.__name__).info(
                    f"List of groups: {str(groups)}"
                )

            await self.wait_for(SearchGroup(["test"], print_groups))
            await self.wait_for(SearchGroup(["awesome"], print_groups))
            await self.wait_for(SearchGroup(["awesome", "cool"], print_groups))
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.SearchGroups())
