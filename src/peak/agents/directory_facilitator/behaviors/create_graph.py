import json

from peak import CyclicBehaviour, Template, getLogger

logger = getLogger(__name__)


class CreateGraph(CyclicBehaviour):
    """Handles the requests to create graphs"""

    async def on_start(self):
        template = Template()
        template.set_metadata("resource", "graph")
        template.set_metadata("action", "create")
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            logger.debug(msg)
            id = msg.get_metadata("id")
            graph = json.loads(msg.get_metadata("graph"))
            self.agent.dataanalysis_data[id] = graph
