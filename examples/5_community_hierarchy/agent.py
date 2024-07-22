from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, OneShotBehaviour, Message, getLogger
logger = getLogger(__name__)

class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def run(self):
            groups_tree = [
                "peak/a0/b0",
                "peak/a0",
                "peak/a1",
                "peak/a2/b2/c0",
                "peak/a1/c3/c1",
            ]
            for groups_branch in groups_tree:
                await self.wait_for(
                    JoinCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)

            # Send a message to a lower hierarchy group
            await self.send_to_lower_hierarchy("A0", "Hello from A0 to B0!")
            await self.receive_message_from_higher_hierarchy()

            for groups_branch in groups_tree:
                await self.wait_for(
                    LeaveCommunity(groups_branch, "conference." + self.agent.jid.domain)
                )
                await sleep(1)
            await self.agent.stop()

        async def send_to_lower_hierarchy(self, current_group: str, message: str):
            lower_group = current_group + "/B0"
            conference_name = lower_group.split("/")[-1] 
            logger.info(f"Sending message to lower hierarchy: {conference_name}")
            muc_jid = f"{conference_name}_down@conference.{self.agent.jid.domain}"
            msg = Message(to=muc_jid)
            msg.body = message
            msg.sender = "a0@conference.localhost"
            await self.send_to_community(msg)
            logger.info(f"Sent message to lower hierarchy: {lower_group}")

        async def receive_message_from_higher_hierarchy(self):
            logger.info("Waiting for message from higher hierarchy")
            msg = await self.receive(timeout=10)
            while True:
                    msg = await self.receive(timeout=10)
                    if msg:
                        if msg.body is not None:
                            logger.info(f"Received text message from higher hierarchy:")
                            logger.info(f"  From: {msg.sender}")
                            logger.info(f"  To: {msg.to}")
                            logger.info(f"  Body: {msg.body}")
                            logger.info(f"  Thread: {msg.thread}")
                            logger.info(f"  Metadata: {msg.metadata}")
                        else:
                            logger.info(f"Received system message:")
                            logger.info(f"  From: {msg.sender}")
                            logger.info(f"  To: {msg.to}")
                            logger.info(f"  Thread: {msg.thread}")
                            logger.info(f"  Metadata: {msg.metadata}")
                    else:
                        logger.info("No message received from higher hierarchy")
                        break

    async def setup(self):
        self.add_behaviour(self.HelloWorld())
