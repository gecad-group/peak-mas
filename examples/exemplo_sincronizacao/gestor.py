import mas 


class Gestor(mas.SyncAgent):
    
    class ReceberConsumos(mas.OneShotBehaviour):
        
        
        async def run(self):
            for _ in range(self.agent.n_agents):
                msg = await self.receive(10)
                if msg:
                    self.agent.consumptio_per_period += int(msg.get_metadata('consumption_value'))

            new_msg = mas.Message()
            new_msg.body = 'Total Consumption: ' + str(self.agent.consumptio_per_period)
            await self.send_to_group(new_msg)
            self.agent.consumptio_per_period = 0

    async def setup(self):
        self.n_agents = 2
        self.consumptio_per_period = 0

    def step(self):
        template = mas.Template()
        template.set_metadata('consumption', '')
        self.add_behaviour(self.ReceberConsumos(), template)


agent = Gestor('Gestor', 'localhost', 'mas')

mas.run(agent)