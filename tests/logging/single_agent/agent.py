from peak import Agent, OneShotBehaviour, getFileLogger, getMainLogger
logger = getFileLogger(__name__)
main_logger = getMainLogger()

class agent(Agent):
    class MyBehaviour(OneShotBehaviour):
        async def run(self):
            logger.info("Hello World!")
            main_logger.info("Hello Terminal!")
            logger.debug("Stoping agent")
            await self.agent.stop()

    async def setup(self):
        logger.info("Agent starting")
        self.add_behaviour(self.MyBehaviour())