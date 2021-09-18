import asyncio
import mas


class AgenteRecetor(mas.Agent):

    def answer(self, sender, message):
        print(message.sender)
        msg = mas.Message()
        msg.body = 'Olá, tudo bem?'
        self.send(msg)

    async def setup(self):
        self.set_message_handler(self.answer)

class AgenteEmissor(mas.Agent):

    class EnviarMensagem(mas.OneShotBehaviour):

        
        async def run(self):
            msg = mas.Message()
            msg.body = 'Boas!'
            self.agent.send(msg)
            await asyncio.sleep(5)

        async def on_end(self):
            msg = mas.Message()
            msg.body = 'Adeus!'
            self.agent.send(msg)
            await self.agent.stop()

    async def setup(self):
        self.add_behaviour(self.EnviarMensagem())

mas_name = 'mas'
server = 'localhost'

recetor = AgenteRecetor('recetor', server, mas_name)

emissor = AgenteEmissor('emissor', server, mas_name)

mas.run(recetor, emissor)