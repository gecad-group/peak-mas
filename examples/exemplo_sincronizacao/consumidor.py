import random
import sys

import mas 


class Consumidor(mas.SyncAgent):
    
    class GerarConsumo(mas.OneShotBehaviour):
        
        
        async def run(self):
            consumption = random.randrange(10, 50)
            msg = mas.Message()
            msg.body= 'my consumption: ' + str(consumption)
            msg.set_metadata('consumption', '')
            msg.set_metadata('consumption_value', str(consumption))
            await self.send_to_group(msg)

    def step(self):
        self.add_behaviour(self.GerarConsumo())

name = sys.argv[1]
agent = Consumidor(name, 'localhost', 'mas')

mas.run(agent)