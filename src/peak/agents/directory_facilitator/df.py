import aiohttp_cors
from aioxmpp import JID

from peak import Agent

from .behaviors import CreateGraph, EcosystemHierarchy, SearchCommunity


class DF(Agent):
    """Directory Facilitator.

    This agent makes available the data that it gathers from multi-agent systems
    publicly through a REST API. It also provides a Yellow Page Service to the
    agents.
    """

    def __init__(self, domain, verify_security, port):
        super().__init__(
            JID.fromstr("df@" + domain + "/admin"), verify_security=verify_security
        )
        self.port = port

    @classmethod
    def name(cls, domain: str) -> str:
        """Retrieves the JID of the DF based on the agent domain.

        Args:
            domain: server's name

        Returns:
            The string of the complete JID of the DF.
        """
        return "df@" + domain + "/admin"

    async def setup(self):
        self.ecosystemhierarchy_data = {
            "nodes": set(),
            "links": set(),
            "categories": set(),
            "node_members": {},
            "tags": {},
        }
        self.dataanalysis_data = dict()
        self.group_tags = dict()

        self.add_behaviour(EcosystemHierarchy())
        self.add_behaviour(SearchCommunity())
        self.add_behaviour(CreateGraph())

        # Create routes.
        self.web.add_get("/groups", self.get_groups, template=None)
        self.web.add_get("/groups/refresh", self.refresh_groups, template=None)
        self.web.add_get("/plots", self.get_plots, template=None)

        # Configure default CORS settings.
        cors = aiohttp_cors.setup(
            self.web.app,
            defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers="*",
                    allow_headers="*",
                )
            },
        )

        # Configure CORS on all routes.
        for route in list(self.web.app.router.routes()):
            cors.add(route)

        # Start web API
        self.web.start("0.0.0.0", port=self.port)
        self.logger.info("REST API running on port " + self.port)

    async def get_groups(self, request):
        return {
            "nodes": list(self.ecosystemhierarchy_data["nodes"]),
            "links": list(self.ecosystemhierarchy_data["links"]),
            "categories": list(self.ecosystemhierarchy_data["categories"]),
            "node_members": self.ecosystemhierarchy_data["node_members"],
        }

    async def refresh_groups(self, request):
        pass

    async def get_plots(self, request):
        return self.dataanalysis_data
