import mas
from mas.jid import name

#O agente aguarda por uma mensagem especifica 'Boas!'
#e reage a essa mensagem
#Se durante 10 segundos nao receber nenhuma mensagem
#o agente desliga-se
class AgenteRecetor(mas.Agent):

    class ReceberMensagem(mas.CyclicBehaviour): #esta Behaviour é executada ciclicamente

        async def run(self):
            msg = await self.receive(10)               #espera 10 segundos até receber uma mensagem
            if msg:
                new_msg = mas.Message()
                new_msg.body = 'Olá, tudo bem ' + name(msg.sender) + '?'
                await self.send_to_group(new_msg)      #envia uma resposta à mensagem que recebeu
            else:
                await self.agent.stop()                #se nao receber uma mensagem desliga o agente
        

    async def setup(self):
        template = mas.Template()
        template.body = 'Boas!'
        self.add_behaviour(self.ReceberMensagem(), template) #o template serve para filtrar o tipo de mensagens a 
                                                             #receber pela Behaviour



agent = AgenteRecetor(name='recetor', server='mas.gecad.isep.ipp.pt', mas_name='mas')

mas.run(agent)