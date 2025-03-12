from peak import Agent, OneShotBehaviour, getFileLogger, getMainLogger, log, debug
file_logger = getFileLogger(__name__)
main_logger = getMainLogger(__name__)

class agent(Agent):
    class MyBehaviour(OneShotBehaviour):
        async def run(self):
            file_logger.info("Hello World!")
            main_logger.debug("Stoping agent")
            await self.agent.stop()

    async def setup(self):
        log("Agent starting")
        debug("One two three")
        self.add_behaviour(self.MyBehaviour())