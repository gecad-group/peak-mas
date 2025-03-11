from peak import Agent, OneShotBehaviour, getLogger
import logging
logger = getLogger(__name__)

class agent(Agent):
    class MyBehaviour(OneShotBehaviour):
        async def run(self):
            logger.info("Hello World!")
            logger.debug("Stoping agent")
            await self.agent.stop()

    async def setup(self):
        logger.info("Agent starting")
        self.add_behaviour(self.MyBehaviour())