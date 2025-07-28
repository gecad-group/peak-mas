import json

from peak import CyclicBehaviour, Template, getLogger

logger = getLogger(__name__)


class EcosystemHierarchy(CyclicBehaviour):
    """Manages the group structure of all the multi-agent systems."""

    async def on_start(self):
        template = Template()
        template.set_metadata("resource", "treehierarchy")
        self.set_template(template)

    async def run(self):
        msg = await self.receive(60)
        if msg:
            logger.debug("message received")
            path = msg.get_metadata("path")
            domain = msg.get_metadata("domain")
            if meta_tags := msg.get_metadata("tags"):
                tags = json.loads(meta_tags)
            nodes = path.split("/")
            logger.debug("nodes: " + str(nodes))
            level = "level"

            if (
                msg.get_metadata("leave")
                and msg.sender
                in self.agent.ecosystemhierarchy_data["node_members"][nodes[-1]]
            ):
                logger.debug(str(msg.sender) + " leaving " + path)
                self.agent.ecosystemhierarchy_data["node_members"][nodes[-1]].remove(
                    msg.sender
                )
                nodes = nodes[::-1]
                # remove empty nodes and links
                for i, node in enumerate(nodes):
                    if len(
                        self.agent.ecosystemhierarchy_data["node_members"][node]
                    ) == 0 and not any(
                        node == source
                        for source, _ in self.agent.ecosystemhierarchy_data["links"]
                    ):
                        self.agent.ecosystemhierarchy_data["node_members"].pop(
                            node
                        )  # this line can be removed, there is no need in removing the node from the dict
                        self.agent.ecosystemhierarchy_data["nodes"].remove(
                            (node, level + str(len(nodes) - 1 - i), domain)
                        )
                        if i + 1 < len(nodes):
                            self.agent.ecosystemhierarchy_data["links"].remove(
                                (nodes[i + 1], node)
                            )
                existing_categories = set()

                # remove categories if empty
                for _, level, _ in self.agent.ecosystemhierarchy_data["nodes"]:
                    existing_categories.add(level)
                difference = self.agent.ecosystemhierarchy_data[
                    "categories"
                ].difference(existing_categories)
                if any(difference):
                    self.agent.ecosystemhierarchy_data["categories"] -= difference

            else:
                logger.debug(str(msg.sender) + " entering " + path)
                last = None
                for i, node in enumerate(nodes):
                    self.agent.ecosystemhierarchy_data["nodes"].add(
                        (node, level + str(i), domain)
                    )
                    if node not in self.agent.ecosystemhierarchy_data["node_members"]:
                        self.agent.ecosystemhierarchy_data["node_members"][node] = []
                    self.agent.ecosystemhierarchy_data["categories"].add(level + str(i))
                    if last != None:
                        self.agent.ecosystemhierarchy_data["links"].add(
                            (
                                last,
                                node,
                            )
                        )
                    last = node
                self.agent.ecosystemhierarchy_data["node_members"][last].append(
                    msg.sender
                )
                for tag in tags:
                    if tag not in self.agent.ecosystemhierarchy_data["tags"]:
                        self.agent.ecosystemhierarchy_data["tags"][tag] = set()
                    self.agent.ecosystemhierarchy_data["tags"][tag].add(last)
