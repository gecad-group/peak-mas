# Standard library imports
import logging
import json
from typing import Callable

# Reader imports
from peak import DF, Message
from peak.core import OneShotBehaviour


class JoinGroup(OneShotBehaviour):
    """Joins a group using a JID."""

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
            await self.agent.join_group(node + "_down@" + self.domain)
        await self.agent.join_group(nodes[-1] + "@" + self.domain)
        await self.agent.join_group(nodes[-1] + "_down@" + self.domain)


class LeaveGroup(OneShotBehaviour):
    """Leaves a group."""

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
            await self.agent.leave_group(node + "_down@" + self.domain)
        await self.agent.leave_group(nodes[-1] + "@" + self.domain)
        await self.agent.leave_group(nodes[-1] + "_down@" + self.domain)


class SearchGroup(OneShotBehaviour):
    """Searches for a group."""

    def __init__(
        self, tags: list[str], callback: Callable[[list[str]], None], *args, **kargs
    ):
        super().__init__()
        self.tags = tags
        self.callback = callback
        self.args = args
        self.kargs = kargs

    async def run(self):
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
        msg.set_metadata("resource", "searchgroup")
        msg.set_metadata("tags", json.dumps(self.tags))
        await self.send(msg)
        res = None
        while not res:
            res = await self.receive(60)
            if not res:
                raise Exception("DF did not respond")
            groups = json.loads(res.get_metadata("groups"))
            logging.getLogger(self.__class__.__name__).debug(
                f"search: {str(self.tags)}, result: {str(groups)}"
            )
            self.callback(self.tags, groups, *self.args, **self.kargs)


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
