import asyncio
import mas

#O agente envia uma mensagem para o grupo MAS
#e espera 5 segundos até se despedir e desligar.
class AgenteEmissor(mas.Agent):

    class EnviarMensagem(mas.OneShotBehaviour):  #Este Behaviour apenas é executado uma vez

        async def run(self):
            msg = mas.Message()
            msg.body = 'Boas!'
            await self.send_to_group(msg, 'mas')  #envia uma mensagem para o grupo MAS
            await asyncio.sleep(5)         #espera segundos
            msg = mas.Message()
            msg.body = 'Adeus!'
            await self.send_to_group(msg)  #envia outra mensagem ao grupo MAS

        async def on_end(self):            #este método é executado antes da Behaviour encerrar
            await self.agent.stop()        #desliga o agente


    async def setup(self):                  #este método é executado antes do agente ser ativado
        self.add_behaviour(self.EnviarMensagem())



agent = AgenteEmissor(name='emissor', server='mas.gecad.isep.ipp.pt', mas_name='mas', group_names={'prosumer', 'buyer'})

mas.run(agent)  #executa os agentes num loop e sai dele quando todos os agentes tiverem sido encerrados