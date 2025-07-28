import json

from peak import CyclicBehaviour, Template, getLogger

logger = getLogger(__name__)


class SearchCommunity(CyclicBehaviour):
    """Handles all the requests to search for groups."""

    async def on_start(self) -> None:
        logger.debug(f"starting {self.__class__.__name__}")
        template = Template()
        template.set_metadata("resource", "searchgroup")
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg and (meta_tags := msg.get_metadata("tags")):
            tags = json.loads(meta_tags)
            communities: set = self.agent.ecosystemhierarchy_data["tags"][tags[0]]
            for tag in tags[1:]:
                communities = communities.intersection(
                    self.agent.ecosystemhierarchy_data["tags"][tag]
                )
            res = msg.make_reply()
            res.set_metadata("communities", json.dumps(list(communities)))
            await self.send(res)
