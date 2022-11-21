# Standard library imports
import logging
from asyncio import sleep

# Reader imports
from peak import Agent, SearchGroup


class group_searcher(Agent):
    async def setup(self) -> None:
        await sleep(3)

        def print_groups(tags, groups):
            logger = logging.getLogger(self.__class__.__name__)
            logger.info(str(tags), str(groups))

        self.add_behaviour(SearchGroup(["test"], print_groups))
        self.add_behaviour(SearchGroup(["awesome"], print_groups))
        self.add_behaviour(SearchGroup(["awesome", "cool"], print_groups))
        await self.stop()
