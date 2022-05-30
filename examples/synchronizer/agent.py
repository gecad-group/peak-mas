from peak.mas import SyncAgent, Message, OneShotBehaviour

import settings

class agent (SyncAgent):

    class SendMessage(OneShotBehaviour):

        async def run(self) -> None:
            msg = Message()
            msg.to = settings.sync_group
            msg.body = 'It\' period ' + str(self.agent.period) + ' and ' + str(self.agent.time) + '.'
            await self.send_to_group(msg)

    async def setup(self) -> None:
        await self.join_group(settings.sync_group)

    async def step(self):
        self.add_behaviour(self.SendMessage())