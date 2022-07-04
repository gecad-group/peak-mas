import aiohttp_cors

from aioxmpp import JID

from peak.mas import Agent
from peak.management.df.functionalities import TreeHierarchy, PubSubCreateNode, CreateGraph, UpdateGraph

import logging

logger = logging.getLogger(__name__)

def df_name(domain):
    return 'df@' + domain + '/admin'

class DF(Agent):

    def __init__(self, domain, verify_security, port):
        super().__init__(JID.fromstr('df@' + domain + '/admin'), verify_security=verify_security)
        self.port = port

    async def setup(self):
        self.treehierarchy_data = dict()
        self.dataanalysis_data = dict()

        self.add_behaviour(TreeHierarchy())
        self.add_behaviour(CreateGraph())
        self.add_behaviour(UpdateGraph())

        self.web.add_get("/tree", self.tree, template=None)
        self.web.add_get("/dataanalysis", self.dataanalysis, template=None)

        # Configure default CORS settings.
        cors = aiohttp_cors.setup(self.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Configure CORS on all routes.
        for route in list(self.web.app.router.routes()):
            cors.add(route)

        # Start web API
        self.web.start(port=self.port)
        logger.info('REST API running on port ' + self.port)

    async def tree(self, request):
        graph = {
            'nodes': list(self.treehierarchy_data['nodes']),
            'links': list(self.treehierarchy_data['links']),
            'categories': list(self.treehierarchy_data['categories']),
            'node_members': self.treehierarchy_data['node_members']
        }
        return graph

    async def tree_refresh(self, request):
        for node, _, domain in self.treehierarchy_data['nodes']:
            group_size = len(await self.group_members(node + '@' + domain))-1
            self.treehierarchy_data['node_members'][node] = group_size
        return self.treehierarchy_data

    async def dataanalysis(self, request):
        return self.dataanalysis_data

