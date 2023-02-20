# Standard library imports
from asyncio import sleep

# Reader imports
from peak import Agent, JoinGroup, LeaveGroup, OneShotBehaviour


class group_admin(Agent):
    class JoinGroups(OneShotBehaviour):
        async def run(self) -> None:
            self.agent.add_behaviour(
                JoinGroup(
                    "group1",
                    f"conference.{self.agent.jid.domain}",
                    ["test", "awesome", "cool"],
                )
            )
            self.agent.add_behaviour(
                JoinGroup(
                    "group2", f"conference.{self.agent.jid.domain}", ["test", "awesome"]
                )
            )
            self.agent.add_behaviour(
                JoinGroup(
                    "group3",
                    f"conference.{self.agent.jid.domain}",
                    [
                        "test",
                    ],
                )
            )
            self.agent.add_behaviour(
                JoinGroup("group4", f"conference.{self.agent.jid.domain}")
            )
            await sleep(10)
            await self.wait_for(
                LeaveGroup("group1", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveGroup("group2", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveGroup("group3", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                LeaveGroup("group4", f"conference.{self.agent.jid.domain}")
            )
            await self.agent.stop()

    async def setup(self) -> None:
        self.add_behaviour(self.JoinGroups())
