import logging
from abc import ABCMeta, abstractmethod
from json import dumps as json_dumps
from typing import Callable

import aioxmpp
import spade.behaviour
from aioxmpp import JID
from spade.message import Message

import peak
from peak import Agent
from peak.df import jid as df_jid

aioxmpp.pubsub.xso.as_payload_class(aioxmpp.Message)


def slice_jid(jid):
    jid = JID.fromstr(jid)
    pubsub = JID.fromstr(jid.domain)
    node = jid.localpart
    return pubsub, node


class _Behaviour:

    agent: Agent

    async def send_to_group(self, msg: Message):
        """Sends a message to a group chat.

        When sending a message to a group the agent joins the group first. The parameter
        'leave' tells the method if the agent leaves, or not, the group after sending the
        message. (If the intention is to send a single request to a new group the best
        option would be to leave the group chat, if the intention is to send a message
        to a group wich the agent already belongs to, it's better to not leave)
        Args:
            msg (mas.Message): The Message.
            group (str, optional): Name of the group to send the message to. If None is given the
                                   the message is sent to the MAS group. Defaults to None.
            leave (bool, optional): If true, agent leaves the group after sending the message. Defaults to False.
        """
        raw_msg = msg.prepare()
        try:
            await self.agent.groups[str(msg.to)].send_message(raw_msg)
        except:
            room, future = self.agent.muc_client.join(msg.to, self.agent.name)
            await future
            await room.send_message(raw_msg)
            await room.leave()

    async def change_node_affiliations(self, jid: str, affiliations_to_set: tuple):
        """Changes PubSub node affiliations.

        Args:
            jid (str): JID of the node, e.g. node@pubsub.example.com
            affiliations_to_set (tuple[str,str]): each tuple must contain the JID of the user and the affiliation (e.g.'owner','publisher')
        """
        pubsub, node = slice_jid(jid)
        user, aff = affiliations_to_set
        await self.agent.pubsub_client.change_node_affiliations(
            pubsub, node, [(JID.fromstr(user), aff)]
        )

    async def subscribe(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.subscribe(pubsub, node)
        await self.agent.pubsub_client.on_item_published.connect(self.on_item_published)

    async def publish(self, msg: Message):
        jid = msg.to.domain
        node = msg.to.localpart
        await self.agent.pubsub_client.publish(JID.fromstr(jid), node, msg.prepare())

    async def notify(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.notify(pubsub, node)

    async def unsubscribe(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.unsubscribe(pubsub, node)

    @abstractmethod
    def on_item_published(jid, node, item, *, message=None):
        pass


class OneShotBehaviour(spade.behaviour.OneShotBehaviour, _Behaviour, metaclass=ABCMeta):
    pass


class PeriodicBehaviour(
    spade.behaviour.PeriodicBehaviour, _Behaviour, metaclass=ABCMeta
):
    pass


class CyclicBehaviour(spade.behaviour.CyclicBehaviour, _Behaviour, metaclass=ABCMeta):
    pass


class FSMBehaviour(spade.behaviour.FSMBehaviour, _Behaviour, metaclass=ABCMeta):
    pass


class JoinGroup(OneShotBehaviour):
    def __init__(self, path: str, domain: str, tags: list = []):
        super().__init__()
        self.path = path
        self.domain = domain
        self.tags = tags

    async def run(self):
        msg = peak.Message()
        msg.to = df_jid(self.agent.jid.domain)
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
    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = peak.Message()
        msg.to = df_jid(self.agent.jid.domain)
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
    def __init__(
        self, tags: list[str], callback: Callable[[list[str]], None], *args, **kargs
    ):
        self.tags = tags
        self.callback = callback
        self.args = args
        self.kargs = kargs

    async def run(self):
        msg = peak.Message()
        msg.to = df_jid(self.agent.jid.domain)
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


class _ExportDataSync(CyclicBehaviour):
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
            msg = peak.Message(to=df_jid(self.agent.jid.domain))
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
                    msg = peak.Message(to=df_jid(self.agent.jid.domain))
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
            msg = peak.Message(to=df_jid(self.agent.jid.domain))
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
            msg = peak.Message(to=df_jid(self.agent.jid.domain))
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
