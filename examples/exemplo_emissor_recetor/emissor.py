import asyncio
import mas


class AgenteEmissor(mas.Agent):

    class EnviarMensagem(mas.OneShotBehaviour):

        async def run(self):
            msg = mas.Message()
            msg.body = 'Boas!'
            await self.send_to_group(msg)
            await asyncio.sleep(5)

        async def on_end(self):
            msg = mas.Message()
            msg.body = 'Adeus!'
            await self.send_to_group(msg)
            await self.agent.stop()


    async def setup(self):
        self.add_behaviour(self.EnviarMensagem())



agent = AgenteEmissor('emissor', 'localhost', 'mas')

mas.run(agent)