import asyncio
from peak import Agent, OneShotBehaviour, getLogger
import ollama

logger = getLogger(__name__)

class agent(Agent):
    class ChatBehaviour(OneShotBehaviour):
        async def run(self):
            model_name = "phi3:mini" 
            prompt = 'Can you write a text (NOT CODE) of an unique Hello World? Use a short reply.'
            logger.info(f"Given prompt: {prompt}")
            try:
                self.pull_model(model_name)
                response = self.generate_response(model_name, prompt)
                logger.info(f"{model_name} response: \n{response['response']}")
            except Exception as e:
                logger.error(f"An error occurred: {e}")
            finally:
                await self.agent.stop()

        def pull_model(self, model_name):
             ollama.pull(model_name)

        def generate_response(self, model_name, prompt_message):
            return ollama.generate(model=model_name, prompt=prompt_message)


    async def setup(self):
        self.add_behaviour(self.ChatBehaviour())