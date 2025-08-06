import json

from peak import DF, Message
from peak.core import OneShotBehaviour


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
