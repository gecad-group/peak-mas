import json
import logging
from typing import Callable

from peak import DF, Message, Template
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


class SearchCommunity(OneShotBehaviour):
    """Searches for a community."""

    def __init__(
        self, tags: list[str], callback: Callable[[list[str]], None], *args, **kargs
    ):
        super().__init__()
        self.tags = tags
        self.callback = callback
        self.args = args
        self.kargs = kargs

    async def on_start(self):
        template = Template()
        template.set_metadata("resource", "searchgroup")
        self.set_template(template)

    async def run(self):
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
        msg.set_metadata("resource", "searchgroup")
        msg.set_metadata("tags", json.dumps(self.tags))
        await self.send(msg)
        res = await self.receive(60)
        if res is None:
            raise Exception("DF did not respond")
        communities = json.loads(res.get_metadata("communities"))
        logging.getLogger(self.__class__.__name__).debug(
            f"search: {str(self.tags)}, result: {str(communities)}"
        )
        self.callback(self.tags, communities, *self.args, **self.kargs)


class CreateGraph(OneShotBehaviour):
    """Creates a graph in the dashboard.

    Sends the graph configuration and data to the DF so he can host it.
    """

    def __init__(self, id: str, graph: dict):
        super().__init__()
        self.id = id
        self.graph = graph

    async def run(self) -> None:
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
        msg.body = f"Create graph {self.id}"
        msg.metadata = {
            "resource": "graph",
            "action": "create",
            "id": self.id,
            "graph": json.dumps(self.graph),
        }
        await self.send(msg)
