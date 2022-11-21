# Standard library imports
from random import random

# Reader imports
from peak import Agent, ExportData, PeriodicBehaviour


class agent(Agent):
    class RandomTrial(PeriodicBehaviour):
        async def on_start(self) -> None:
            self.count = 0

        async def run(self) -> None:
            if self.count >= 10:
                await self.agent.stop()
            self.agent.x = [self.count, random() * 100]
            self.agent.y = [self.count, random() * 100]
            self.agent.z = [self.count, random() * 100]
            self.count += 1

    async def setup(self) -> None:
        self.x = 0
        self.y = 0
        self.z = 0
        self.add_behaviour(self.RandomTrial(1))
        self.add_behaviour(
            ExportData(
                "output.json",
                ["x", "y", "z"],
                interval=2,
                to_graph=True,
                graph_name=self.name,
            )
        )
