import asyncio
from peak import Agent, OneShotBehaviour, getLogger
import ollama

logger = getLogger(__name__)

class Bot(Agent):
    class ChatBehaviour(OneShotBehaviour):
        async def run(self):
            model_name = "phi3:mini"  # Using latest version of Phi
            prompt = 'Can you say a text (NOT CODE) of an unique Hello World? Use 20 words or less.'
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
            logger.info(f"Pulling model {model_name}...")
            ollama_model = ollama.pull(model_name)
            logger.info(f"Model {model_name} pulled {ollama_model}")

        def generate_response(self, model_name, prompt_message):
            logger.info(f"Generating response using {model_name}...")
            return ollama.generate(model=model_name, prompt=prompt_message)


    async def setup(self):
        self.add_behaviour(self.ChatBehaviour())