import json
import logging
from typing import Callable

from peak import DF, Message, Template
from peak.core import OneShotBehaviour


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
