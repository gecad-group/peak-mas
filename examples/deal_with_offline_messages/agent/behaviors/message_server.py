from peak import CyclicBehaviour, Message


class MessageServer(CyclicBehaviour):
    async def run(self):
        msg = await self.receive()
        print(f"Received message: {msg}")
        Message()
