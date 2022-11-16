from asyncio import sleep
from peak import Agent, JoinGroup, LeaveGroup


class group_admin(Agent):
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
        await sleep(10)
        self.add_behaviour(LeaveGroup("group1", "conference.localhost"))
        self.add_behaviour(LeaveGroup("group2", "conference.localhost"))
        self.add_behaviour(LeaveGroup("group3", "conference.localhost"))
        self.add_behaviour(LeaveGroup("group4", "conference.localhost"))
        await self.stop()
