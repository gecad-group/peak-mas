from peak import DF, Message
from peak.core import OneShotBehaviour


class LeaveCommunity(OneShotBehaviour):
    """Leaves a community."""

    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
        msg.set_metadata("resource", "treehierarchy")
        msg.set_metadata("path", self.path)
        msg.set_metadata("domain", self.domain)
        msg.set_metadata("leave", "true")
        await self.send(msg)
        nodes = self.path.split("/")
        for node in nodes[:-1]:
            await self.leave_community(node + "_down@" + self.domain)
        await self.leave_community(nodes[-1] + "@" + self.domain)
        await self.leave_community(nodes[-1] + "_down@" + self.domain)
