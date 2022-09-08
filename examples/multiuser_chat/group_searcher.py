import logging

from peak.mas import Agent, JoinGroup, SearchGroup


class group_searcher(Agent):
    async def setup(self) -> None:
        self.add_behaviour(
            JoinGroup("group1", "conference.localhost", ["test", "awesome", "cool"])
        )
        self.add_behaviour(
            JoinGroup("group2", "conference.localhost", ["test", "awesome"])
        )
        self.add_behaviour(
            JoinGroup(
                "group3",
                "conference.localhost",
                [
                    "test",
                ],
            )
        )
        self.add_behaviour(JoinGroup("group4", "conference.localhost"))
        logger = logging.getLogger(self.__class__.__name__)

        def print_groups(tags, groups):
            logger.info(str(tags), str(groups))

        self.add_behaviour(SearchGroup(["test"], print_groups))
        self.add_behaviour(SearchGroup(["awesome"], print_groups))
        self.add_behaviour(SearchGroup(["awesome", "cool"], print_groups))
