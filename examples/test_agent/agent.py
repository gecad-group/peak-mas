from asyncio import sleep

from peak import Agent, JoinCommunity, LeaveCommunity, Message, OneShotBehaviour


class agent(Agent):
    class HelloWorld(OneShotBehaviour):
        async def on_start(self):
            await self.wait_for(
                JoinCommunity("group1", f"conference.{self.agent.jid.domain}")
            )
            await self.wait_for(
                JoinCommunity("group2", f"conference.{self.agent.jid.domain}")
            )

        async def run(self):
            msg = Message(to=f"group1@conference.{self.agent.jid.domain}")
            msg.body = "Hello World"
            await self.send_to_community(msg)
            await sleep(5)
            #await sleep(30)
            msg.body = "Goodbye World"
            await self.send_to_community(msg)
            self.kill()

        async def on_end(self):
            await self.agent.stop()
            #communities = self.agent.communities.copy()
            #print("################")
            #print(communities)
            #print("################")

            #for community in communities:
                #print("AAAAAAAAAAAAAAAA")
                #print(community)
                #print("AAAAAAAAAAAAAAAA")
                #await self.leave_community(community)
                # self._logger.debug("Left all communities")



    async def setup(self):
        self.add_behaviour(self.HelloWorld())
