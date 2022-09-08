import logging
from json import dumps as json_dumps
from typing import Callable

import peak.mas as peak
from peak.management.df.df import df_name


class CreateNode(peak.OneShotBehaviour):
    def __init__(self, node: str, affiliation: str = None):
        super().__init__()
        self.affiliation = affiliation
        self.node = node

    async def on_start(self):
        self.template = peak.Template()
        self.template.set_metadata("resource", "pubsub_create_node")

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata("resource", "pubsub_create_node")
        msg.set_metadata("affiliation", self.affiliation if self.affiliation else "")
        msg.set_metadata("node_jid", self.node)
        await self.send(msg)
        res = await self.receive(60)
        if res:
            logger = logging.getLogger("CreateNode")
            logger.info("PubSub node " + self.node + " created")


class JoinGroup(peak.OneShotBehaviour):
    def __init__(self, path: str, domain: str, tags: list = []):
        super().__init__()
        self.path = path
        self.domain = domain
        self.tags = tags

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata("resource", "treehierarchy")
        msg.set_metadata("path", self.path)
        msg.set_metadata("domain", self.domain)
        msg.set_metadata("tags", str(self.tags))
        await self.send(msg)
        nodes = self.path.split("/")
        for node in nodes[:-1]:
            await self.agent.join_group(node + "_down@" + self.domain)
        await self.agent.join_group(nodes[-1] + "@" + self.domain)
        await self.agent.join_group(nodes[-1] + "_down@" + self.domain)


class LeaveGroup(peak.OneShotBehaviour):
    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
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


class SearchGroup(peak.OneShotBehaviour):
    def __init__(
        self, tags: list[str], callback: Callable[[list[str]], None], *args, **kargs
    ):
        self.tags = tags
        self.callback = callback
        self.args = args
        self.kargs = kargs

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata("resource", "searchgroup")
        msg.set_metadata("tags", str(self.tags))
        await self.send(msg)
        res = None
        while not res:
            res = await self.receive(60)
            if not res:
                raise Exception("DF did not respond")
            groups = res.get_metadata("groups")
            logging.getLogger(self.__class__.__name__).info(self.tags, groups)
            self.callback(self.tags, groups, *self.args, **self.kargs)


class ExportData(peak.OneShotBehaviour):
    def __init__(
        self,
        file_name: str,
        properties: list,
        interval: int = None,
        to_graph: bool = False,
        graph_name: str = "",
        graph_options: str = "",
    ):
        super().__init__()
        self.interval = interval
        self.file_name = file_name
        self.properties = properties
        self.to_graph = to_graph
        if graph_name == "" and self.to_graph:
            raise Exception("if graph is set to true, it must have a name")
        self.graph_name = graph_name
        self.graph_options = graph_options

    async def run(self) -> None:
        logger = logging.getLogger(self.__class__.__name__)
        if isinstance(self.agent, peak.SyncAgent):
            logger.debug("synchronizer detected")
            self.agent.add_behaviour(
                _ExportDataSync(
                    self.file_name,
                    self.properties,
                    self.to_graph,
                    self.graph_name,
                    self.graph_options,
                )
            )
        else:
            logger.debug("synchronizer not detected")
            self.agent.add_behaviour(
                _ExportData(
                    self.file_name,
                    self.properties,
                    self.interval,
                    self.to_graph,
                    self.graph_name,
                    self.graph_options,
                )
            )


class _ExportDataSync(peak.CyclicBehaviour):
    def __init__(
        self,
        file_name: str,
        properties: list,
        to_graph: bool,
        graph_name: str,
        graph_options: str,
    ):
        super().__init__()
        self.file_name = file_name
        self.graph_name = graph_name
        self.properties = properties
        self.to_graph = to_graph
        self.graph_options = graph_options

    async def on_start(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("behaviour initiated")
        template_step = peak.Template()
        template_step.set_metadata("sync", "step")
        template_stop = peak.Template()
        template_stop.set_metadata("sync", "stop")
        template = template_step | template_stop
        self.set_template(template)

        self.file_data = {}
        for property in self.properties:
            self.file_data[property] = []
        if self.to_graph:
            msg = peak.Message(to=df_name(self.agent.jid.domain))
            msg.body = "Create graph " + self.graph_name
            msg.metadata = {
                "resource": "graph",
                "action": "create",
                "graph_name": self.graph_name,
                "graph_options": self.graph_options,
                "properties": json_dumps(self.properties),
            }
            await self.send(msg)
            self.logger.info("creating graph " + +self.graph_name)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            if msg.get_metadata("sync") == "step":
                current_data = dict()
                for property in self.file_data:
                    attribute = getattr(self.agent, property)
                    if type(attribute) is peak.Property:
                        self.file_data[property].append(attribute.current_value)
                        current_data[property] = attribute.current_value
                    else:
                        self.file_data[property].append(attribute)
                        current_data[property] = attribute
                if self.to_graph:
                    msg = peak.Message(to=df_name(self.agent.jid.domain))
                    msg.body = "Update graph " + self.file_name
                    msg.metadata = {
                        "resource": "graph",
                        "action": "update",
                        "graph_name": self.file_name,
                        "data": json_dumps(current_data),
                    }
                    await self.send(msg)
                    self.logger.info("updating graph " + +self.graph_name)
            if msg.get_metadata("sync") == "stop":
                with open(self.file_name, "w") as f:
                    f.write(json_dumps(self.data))


class _ExportData(peak.PeriodicBehaviour):
    def __init__(
        self,
        file_name: str,
        properties: list,
        interval: float,
        to_graph: bool,
        graph_name: str,
        graph_options: str,
    ):
        super().__init__(interval, None)
        self.file_name = file_name
        self.graph_name = graph_name
        self.properties = properties
        self.to_graph = to_graph
        self.graph_options = graph_options

    async def on_start(self) -> None:
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info("exporting " + str(self.properties))
        self.file_data = {}
        for property in self.properties:
            self.file_data[property] = []
        if self.to_graph:
            msg = peak.Message(to=df_name(self.agent.jid.domain))
            msg.body = "Create graph " + self.graph_name
            msg.metadata = {
                "resource": "graph",
                "action": "create",
                "graph_name": self.graph_name,
                "graph_options": self.graph_options,
                "properties": json_dumps(self.properties),
            }
            await self.send(msg)
            self.logger.info("creating graph " + self.graph_name)

    async def run(self) -> None:
        current_data = dict()
        for property in self.file_data:
            attribute = getattr(self.agent, property)
            if type(attribute) is peak.Property:
                self.file_data[property].append(attribute.current_value)
                current_data[property] = attribute.current_value
            else:
                self.file_data[property].append(attribute)
                current_data[property] = attribute
            self.logger.debug(
                'exporting property "' + property + '": ' + str(current_data[property])
            )
        if self.to_graph:
            msg = peak.Message(to=df_name(self.agent.jid.domain))
            msg.body = "Update graph " + self.graph_name
            msg.metadata = {
                "resource": "graph",
                "action": "update",
                "graph_name": self.graph_name,
                "data": json_dumps(current_data),
            }
            await self.send(msg)
            self.logger.debug("updating graph " + self.graph_name)

    async def on_end(self) -> None:
        self.logger.info('exporting to file "' + self.file_name + '"')
        with open(self.file_name, "w") as f:
            f.write(json_dumps(self.file_data))
