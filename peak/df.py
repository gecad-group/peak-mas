import logging
from json import loads as json_loads

import aiohttp_cors
from aioxmpp import JID

from peak import Agent, CyclicBehaviour, Template

logger = logging.getLogger(__name__)


def jid(domain):
    return "df@" + domain + "/admin"


class DF(Agent):
    def __init__(self, domain, verify_security, port):
        super().__init__(
            JID.fromstr("df@" + domain + "/admin"), verify_security=verify_security
        )
        self.port = port

    async def setup(self):
        self.treehierarchy_data = dict()
        self.dataanalysis_data = dict()
        self.group_tags = dict()

        self.add_behaviour(TreeHierarchy())
        self.add_behaviour(CreateGraph())
        self.add_behaviour(UpdateGraph())

        self.web.add_get("/tree", self.tree, template=None)
        self.web.add_get("/dataanalysis", self.dataanalysis, template=None)

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
        self.web.start(port=self.port)
        logger.info("REST API running on port " + self.port)

    async def tree(self, request):
        graph = {
            "nodes": list(self.treehierarchy_data["nodes"]),
            "links": list(self.treehierarchy_data["links"]),
            "categories": list(self.treehierarchy_data["categories"]),
            "node_members": self.treehierarchy_data["node_members"],
        }
        return graph

    async def tree_refresh(self, request):
        for node, _, domain in self.treehierarchy_data["nodes"]:
            group_size = len(await self.group_members(node + "@" + domain)) - 1
            self.treehierarchy_data["node_members"][node] = group_size
        return self.treehierarchy_data

    async def dataanalysis(self, request):
        return self.dataanalysis_data


class TreeHierarchy(CyclicBehaviour):
    async def on_start(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("starting behaviour")
        template = Template()
        template.set_metadata("resource", "treehierarchy")
        self.set_template(template)
        self.agent.treehierarchy_data = {
            "nodes": set(),
            "links": set(),
            "categories": set(),
            "node_members": {},
            "tags": {},
        }

    async def run(self):
        msg = await self.receive(60)
        if msg:
            self.logger.debug("message received")
            path = msg.get_metadata("path")
            domain = msg.get_metadata("domain")
            tags = json_loads(msg.get_metadata("tags"))
            nodes = path.split("/")
            self.logger.debug("nodes: " + str(nodes))
            level = "level"

            if (
                msg.get_metadata("leave")
                and msg.sender
                in self.agent.treehierarchy_data["node_members"][nodes[-1]]
            ):
                self.logger.debug(str(msg.sender) + " leaving " + path)
                self.agent.treehierarchy_data["node_members"][nodes[-1]].remove(
                    msg.sender
                )
                nodes = nodes[::-1]
                # remove empty nodes and links
                for i, node in enumerate(nodes):
                    if len(
                        self.agent.treehierarchy_data["node_members"][node]
                    ) == 0 and not any(
                        node == source
                        for source, _ in self.agent.treehierarchy_data["links"]
                    ):
                        self.agent.treehierarchy_data["node_members"].pop(node)
                        self.agent.treehierarchy_data["nodes"].remove(
                            (node, level + str(len(nodes) - 1 - i), domain)
                        )
                        if i + 1 < len(nodes):
                            self.agent.treehierarchy_data["links"].remove(
                                (nodes[i + 1], node)
                            )
                existing_categories = set()

                # remove categories if empty
                for _, level, _ in self.agent.treehierarchy_data["nodes"]:
                    existing_categories.add(level)
                difference = self.agent.treehierarchy_data["categories"].difference(
                    existing_categories
                )
                if any(difference):
                    self.agent.treehierarchy_data["categories"] -= difference

            else:
                self.logger.debug(str(msg.sender) + " entering " + path)
                last = None
                for i, node in enumerate(nodes):
                    if node not in self.agent.treehierarchy_data["node_members"]:
                        self.agent.treehierarchy_data["node_members"][node] = []
                    self.agent.treehierarchy_data["nodes"].add(
                        (node, level + str(i), domain)
                    )
                    self.agent.treehierarchy_data["categories"].add(level + str(i))
                    if last != None:
                        self.agent.treehierarchy_data["links"].add(
                            (
                                last,
                                node,
                                max(
                                    len(
                                        self.agent.treehierarchy_data["node_members"][
                                            last
                                        ]
                                    )
                                    + 1,
                                    len(
                                        self.agent.treehierarchy_data["node_members"][
                                            node
                                        ]
                                    ),
                                ),
                            )
                        )
                    last = node
                self.agent.treehierarchy_data["node_members"][last].append(msg.sender)
                for tag in tags:
                    if tag not in self.agent.treehierarchy_data["tags"]:
                        self.agent.treehierarchy_data["tags"][tag] = set()
                    self.agent.treehierarchy_data["tags"][tag].add(last)


class SearchGroup(CyclicBehaviour):
    async def on_start(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("starting behaviour")
        template = Template()
        template.set_metadata("resource", "searchgroup")
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            tags = json_loads(msg.get_metadata("tags"))
            groups = self.agent.treehierarchy_data["tags"][tags[0]]
            for tag in tags[1:]:
                groups.intersection(self.agent.treehierarchy_data["tags"][tag])
            res = msg.make_reply()
            res.set_metadata("groups", groups)
            await self.send(res)


class CreateGraph(CyclicBehaviour):
    async def on_start(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("starting behaviour")
        template = Template()
        template.set_metadata("resource", "graph")
        template.set_metadata("action", "create")
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            self.logger.debug(msg.body)
            graph_name = msg.get_metadata("graph_name")
            graph_options = msg.get_metadata("graph_options")
            properties = json_loads(msg.get_metadata("properties"))
            self.agent.dataanalysis_data[graph_name] = {
                "graph_options": graph_options,
                "data": {},
            }
            for property in properties:
                self.agent.dataanalysis_data[graph_name]["data"][property] = []


class UpdateGraph(CyclicBehaviour):
    async def on_start(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.debug("starting behaviour")
        template = Template()
        template.set_metadata("resource", "graph")
        template.set_metadata("action", "update")
        self.set_template(template)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            self.logger.debug(msg.body)
            graph_name = msg.get_metadata("graph_name")
            data = json_loads(msg.get_metadata("data"))
            for property in data:
                self.agent.dataanalysis_data[graph_name]["data"][property].append(
                    data[property]
                )
                self.logger.debug(
                    'updating property "' + property + '" : ' + str(data[property])
                )
