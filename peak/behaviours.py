import logging
from json import dumps as json_dumps
from typing import Callable

from peak import Message, SyncAgent, Template, DF
from peak.core import CyclicBehaviour, OneShotBehaviour, PeriodicBehaviour
from peak.properties import Property


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
        msg.set_metadata("tags", str(self.tags))
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
        self.tags = tags
        self.callback = callback
        self.args = args
        self.kargs = kargs

    async def run(self):
        msg = Message()
        msg.to = DF.name(self.agent.jid.domain)
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


class ExportData(OneShotBehaviour):
    """Exports data to a file and optionaly to the DF.

    The data exports works diferently when using the Synchronizer and
    when its not used. When the Synchronizer its being used the data
    is exported at the same rate as the Synchronizers clock. If its not
    used the user must define a interval in which the data is exported."""

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
            raise Exception("when graph is set to true, a name for it must be defined")
        self.graph_name = graph_name
        self.graph_options = graph_options

    async def run(self) -> None:
        logger = logging.getLogger(self.__class__.__name__)
        if isinstance(self.agent, SyncAgent):
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


class _ExportDataSync(CyclicBehaviour):
    """Exports the data at the same rate as the synchronization."""

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
        template_step = Template()
        template_step.set_metadata("sync", "step")
        template_stop = Template()
        template_stop.set_metadata("sync", "stop")
        template = template_step | template_stop
        self.set_template(template)

        self.file_data = {}
        for property in self.properties:
            self.file_data[property] = []
        if self.to_graph:
            msg = Message(to=DF.name(self.agent.jid.domain))
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
                    if type(attribute) is Property:
                        self.file_data[property].append(attribute.current_value)
                        current_data[property] = attribute.current_value
                    else:
                        self.file_data[property].append(attribute)
                        current_data[property] = attribute
                if self.to_graph:
                    msg = Message(to=DF.name(self.agent.jid.domain))
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


class _ExportData(PeriodicBehaviour):
    """Exports the data at a rate defined by the user."""

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
            msg = Message(to=DF.name(self.agent.jid.domain))
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
            if type(attribute) is Property:
                self.file_data[property].append(attribute.current_value)
                current_data[property] = attribute.current_value
            else:
                self.file_data[property].append(attribute)
                current_data[property] = attribute
            self.logger.debug(
                'exporting property "' + property + '": ' + str(current_data[property])
            )
        if self.to_graph:
            msg = Message(to=DF.name(self.agent.jid.domain))
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
