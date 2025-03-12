import ollama

from peak import Agent, CyclicBehaviour

model_name = "phi3:mini"


class assistant(Agent):
    class ChatBehaviour(CyclicBehaviour):
        async def run(self):
            message = await self.receive()
            llm_response = ollama.generate(model_name, message.body)
            print(llm_response)
            reply = message.make_reply()
            reply.body = llm_response["response"]
            await self.send(reply)

    async def setup(self):
        self.add_behaviour(self.ChatBehaviour())
