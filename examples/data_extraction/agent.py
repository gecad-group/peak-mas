import json
from random import random

from peak import Agent, CreateGraph, PeriodicBehaviour


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
            with open("graph_options.json") as file:
                self.graph = json.load(file)

        async def run(self) -> None:
            if self.count >= 10:
                await self.agent.stop()
            consumption = [
                self.count,
                self.consumption_data[self.count] * 1000 + random() * 100,
            ]
            generation = [
                self.count,
                self.generation_data[self.count] * 1000 + random() * 100,
            ]
            self.graph["series"][0]["data"].append(consumption)
            self.graph["series"][1]["data"].append(generation)
            self.agent.add_behaviour(CreateGraph("house", self.graph))
            self.count += 1

    async def setup(self) -> None:
        self.add_behaviour(self.RandomTrial(5))
