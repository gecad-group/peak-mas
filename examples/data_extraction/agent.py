# Standard library imports
from random import random

# Reader imports
from peak import Agent, ExportData, PeriodicBehaviour


class agent(Agent):
    class RandomTrial(PeriodicBehaviour):
        async def on_start(self) -> None:
            self.count = 0
            self.consumption_data = [
                2.322958984,
                2.371797342,
                2.415960996,
                2.302537907,
                2.363063026,
                2.334030652,
                2.299585462,
                2.316069946,
                2.341042708,
                2.402921031,
                2.342395912,
            ]
            self.generation_data = [
                0.017204275,
                0.039324056,
                0.052104375,
                0.063410041,
                0.073241055,
                0.081597417,
                0.089953779,
                0.095360837,
                0.103225648,
                0.198094934,
                0.373578536,
            ]

        async def run(self) -> None:
            if self.count >= 10:
                await self.agent.stop()
            self.agent.consumption = [
                self.count,
                self.consumption_data[self.count] * 1000 + random() * 100,
            ]
            self.agent.generation = [
                self.count,
                self.generation_data[self.count] * 1000 + random() * 100,
            ]
            self.count += 1

    async def setup(self) -> None:
        self.consumption = 0
        self.generation = 0
        self.add_behaviour(self.RandomTrial(1))
        self.add_behaviour(
            ExportData(
                "output.json",
                ["consumption", "generation"],
                interval=1,
                to_graph=True,
                graph_name=self.name,
            )
        )
