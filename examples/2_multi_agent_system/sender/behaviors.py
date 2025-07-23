from peak import Message, OneShotBehaviour


class SendHelloWorld(OneShotBehaviour):
    async def run(self):
        msg = Message(
            to=f"harry@{self.agent.jid.domain}",
            body="Hello World",
            thread="12345",  # Optional thread ID
            metadata={"performative": "inform"},
        )
        await self.send(msg)
        await self.agent.stop()
