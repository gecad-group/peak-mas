import mas
from mas.message import name


class AgenteRecetor(mas.Agent):

    class ReceberMensagem(mas.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(10)
            if msg:
                new_msg = mas.Message()
                new_msg.body = 'Olá, tudo bem ' + name(msg.sender) + '?'
                await self.send_to_group(new_msg) 
            else:
                await self.agent.stop()
        

    async def setup(self):
        template = mas.Template()
        template.body = 'Boas!'
        self.add_behaviour(self.ReceberMensagem(), template)



agent = AgenteRecetor('recetor', 'localhost', 'mas')


mas.run(agent)