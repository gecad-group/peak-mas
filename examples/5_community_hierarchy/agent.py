from asyncio import sleep

from peak import (
    Agent,
    JoinCommunity,
    LeaveCommunity,
    Message,
    OneShotBehaviour,
    getLogger,
)

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

        async def send_to_lower_hierarchy(self, group: str, message: str):
            logger.info(f"Sending message to lower hierarchy: {group}")
            muc_jid = f"{group}_down@conference.{self.agent.jid.domain}"
            msg = Message(to=muc_jid)
            msg.body = message
            await self.send_to_community(msg)
            logger.info(f"Sent message to lower hierarchy: {group}")

        async def receive_message_from_higher_hierarchy(self):
            logger.info("Waiting for message from higher hierarchy")
            while True:
                msg = await self.receive()
                if msg:
                    if msg.body is not None:
                        logger.info(f"Received text message from higher hierarchy:")
                        logger.info(f"  From: {msg.sender}")
                        logger.info(f"  To: {msg.to}")
                        logger.info(f"  Body: {msg.body}")
                        logger.info(f"  Thread: {msg.thread}")
                        logger.info(f"  Metadata: {msg.metadata}")
                        break
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
