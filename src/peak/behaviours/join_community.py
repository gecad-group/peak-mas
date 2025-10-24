import json

from peak import DF, Message
from peak.core import OneShotBehaviour


class JoinCommunity(OneShotBehaviour):
    """Joins a community using a JID."""

    def __init__(self, path: str, domain: str, tags: list = []):
        super().__init__()
        self.path = path
        self.domain = domain
        self.tags = tags

    async def run(self):
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
        msg.set_metadata("resource", "treehierarchy")
        msg.set_metadata("path", self.path)
        msg.set_metadata("domain", self.domain)
        msg.set_metadata("tags", json.dumps(self.tags))
        await self.send(msg)
        nodes = self.path.split("/")
        for node in nodes[:-1]:
            await self.join_community(node + "_down@" + self.domain)
        await self.join_community(nodes[-1] + "_down@" + self.domain)
        await self.join_community(nodes[-1] + "@" + self.domain)
