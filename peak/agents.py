import asyncio as _asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from abc import abstractmethod
from datetime import datetime, timedelta
from json import loads as json_loads

import aiohttp_cors
from aioxmpp import JID

from peak import Agent, CyclicBehaviour, Message, PeriodicBehaviour, Template

_logger = _logging.getLogger(__name__)


class SyncAgent(Agent, metaclass=_ABCMeta):
    class _StepBehaviour(CyclicBehaviour):
        """Listens for the Synchronizer messages."""

        async def on_start(self):
            _logger.info("Waiting for simulation to start...")

        async def run(self):
            msg = await self.receive(10)
            if msg:
                if msg.get_metadata("sync") == "step":
                    self.agent.period = int(msg.get_metadata("period"))
                    self.agent.time = datetime.strptime(
                        msg.get_metadata("time"), "%Y-%m-%d %H:%M:%S"
                    )
                    if self.agent.period != 0:
                        self.agent.iterate_properties()
                    await self.agent.step()
                    _logger.info(
                        "Period "
                        + str(self.agent.period)
                        + " ("
                        + str(self.agent.time)
                        + ")"
                    )
                if msg.get_metadata("sync") == "stop":
                    _logger.info("Simulation ended")
                    self.kill()

        async def on_end(self):
            await self.agent.stop()

    def __init__(self, jid: JID, properties=None, verify_security=False):
        """Agent that listens to the Synchronizer.

        This is an abstract class. Step method must be overriden.

        Args:
            name (str): Name of the agent.
            server (str): Domain of the XMPP server to connect to.
            mas_name (str): Name of the MAS to be used to join a group chat between the agents.
            group_names (set[str], optional): Set of group names to join to. Defaults to {}.
            verify_security (bool, optional): Wether to verify or not the SSL certificates. Defaults to False.
        """
        super().__init__(jid, properties, verify_security)
        self.period = 0
        self.time = None
        template_step = Template()
        template_step.set_metadata("sync", "step")
        template_stop = Template()
        template_stop.set_metadata("sync", "stop")
        template = template_step | template_stop
        self.add_behaviour(self._StepBehaviour(), template)

    @abstractmethod
    async def step(self):
        """This method is executed at each step.

        It must be overriden.

        Raises:
            NotImplementedError: The step method must be overriden.
        """
        raise NotImplementedError("The step method must be overriden.")


class Synchronizer(Agent):
    class _StepBehaviour_old(PeriodicBehaviour):
        """Sends a message to MAS group for each step."""

        def __init__(
            self,
            group_jid,
            n_agents: int,
            periods: int,
            time_per_period: float,
            start_at=None,
        ):
            super().__init__(time_per_period, start_at=start_at)
            self.group_jid = group_jid
            self.n_agents = n_agents
            self.periods = periods

        async def on_start(self):
            while not len(self.agent.group_members(self.group_jid)) >= self.n_agents:
                await _asyncio.sleep(1)
            self.current_period = 0
            _logger.info("Starting simulation...")

        async def run(self):
            msg = Message()
            msg.to = self.group_jid
            if self.current_period >= self.periods:
                msg.set_metadata("sync", "stop")
                self.kill()
            else:
                _logger.info("Period " + str(self.current_period))
                msg.body = "Period " + str(self.current_period)
                msg.set_metadata("sync", "step")
                msg.set_metadata("period", str(self.current_period))
            await self.send_to_group(msg)
            self.current_period += 1

        async def on_end(self):
            _logger.info("Ending simulation...")
            await self.agent.stop()

    class _StepBehaviour(PeriodicBehaviour):
        """Sends a message to MAS group for each step."""

        def __init__(
            self,
            jid,
            n_agents: int,
            initial_time: datetime,
            end_time: datetime,
            period_time_simulated: timedelta,
            period_time_real: float,
            start_at: datetime = None,
        ):
            super().__init__(period_time_real, start_at=start_at)
            self.group_jid = jid
            self.n_agents = n_agents
            self.time = initial_time
            self.end_time = end_time
            self.period_time = period_time_simulated

        async def on_start(self):
            _logger.info("Waiting for all agents to enter the group...")
            while (
                not len(await self.agent.group_members(self.group_jid)) >= self.n_agents
            ):
                await _asyncio.sleep(1)
            self.current_period = 0
            _logger.info("Starting simulation...")

        async def run(self):
            msg = Message()
            msg.to = self.group_jid
            if self.time >= self.end_time:
                msg.set_metadata("sync", "stop")
                self.kill()
            else:
                _logger.info(
                    "Period " + str(self.current_period) + " (" + str(self.time) + ")"
                )
                msg.body = (
                    "Period " + str(self.current_period) + " (" + str(self.time) + ")"
                )
                msg.set_metadata("sync", "step")
                msg.set_metadata("period", str(self.current_period))
                msg.set_metadata(
                    "time", datetime.strftime(self.time, "%Y-%m-%d %H:%M:%S")
                )
            await self.send_to_group(msg)
            self.current_period += 1
            self.time += self.period_time

        async def on_end(self):
            _logger.info("Ending simulation...")
            await self.agent.stop()

    async def sync_group(
        self, jid, n_agents: int, time_per_period: float, periods: int
    ):
        await self.join_group(jid)
        self.add_behaviour(
            self._StepBehaviour_old(jid, n_agents, periods, time_per_period)
        )

    async def sync_group(
        self,
        jid,
        n_agents: int,
        initial_time: datetime,
        end_time: datetime,
        period_time_simulated: timedelta,
        period_time_real: float,
        start_at: datetime = None,
    ):
        await self.join_group(jid)
        self.add_behaviour(
            self._StepBehaviour(
                jid,
                n_agents,
                initial_time,
                end_time,
                period_time_simulated,
                period_time_real,
                start_at,
            )
        )


class DF(Agent):
    class GroupHierarchy(CyclicBehaviour):
        async def on_start(self):
            self.logger = _logging.getLogger(self.__class__.__name__)
            self.logger.debug("starting behaviour")
            template = Template()
            template.set_metadata("resource", "treehierarchy")
            self.set_template(template)
            self.agent.grouphierarchy_data = {
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
                    in self.agent.grouphierarchy_data["node_members"][nodes[-1]]
                ):
                    self.logger.debug(str(msg.sender) + " leaving " + path)
                    self.agent.grouphierarchy_data["node_members"][nodes[-1]].remove(
                        msg.sender
                    )
                    nodes = nodes[::-1]
                    # remove empty nodes and links
                    for i, node in enumerate(nodes):
                        if len(
                            self.agent.grouphierarchy_data["node_members"][node]
                        ) == 0 and not any(
                            node == source
                            for source, _ in self.agent.grouphierarchy_data["links"]
                        ):
                            self.agent.grouphierarchy_data["node_members"].pop(node)
                            self.agent.grouphierarchy_data["nodes"].remove(
                                (node, level + str(len(nodes) - 1 - i), domain)
                            )
                            if i + 1 < len(nodes):
                                self.agent.grouphierarchy_data["links"].remove(
                                    (nodes[i + 1], node)
                                )
                    existing_categories = set()

                    # remove categories if empty
                    for _, level, _ in self.agent.grouphierarchy_data["nodes"]:
                        existing_categories.add(level)
                    difference = self.agent.grouphierarchy_data[
                        "categories"
                    ].difference(existing_categories)
                    if any(difference):
                        self.agent.grouphierarchy_data["categories"] -= difference

                else:
                    self.logger.debug(str(msg.sender) + " entering " + path)
                    last = None
                    for i, node in enumerate(nodes):
                        if node not in self.agent.grouphierarchy_data["node_members"]:
                            self.agent.grouphierarchy_data["node_members"][node] = []
                        self.agent.grouphierarchy_data["nodes"].add(
                            (node, level + str(i), domain)
                        )
                        self.agent.grouphierarchy_data["categories"].add(level + str(i))
                        if last != None:
                            self.agent.grouphierarchy_data["links"].add(
                                (
                                    last,
                                    node,
                                    max(
                                        len(
                                            self.agent.grouphierarchy_data[
                                                "node_members"
                                            ][last]
                                        )
                                        + 1,
                                        len(
                                            self.agent.grouphierarchy_data[
                                                "node_members"
                                            ][node]
                                        ),
                                    ),
                                )
                            )
                        last = node
                    self.agent.grouphierarchy_data["node_members"][last].append(
                        msg.sender
                    )
                    for tag in tags:
                        if tag not in self.agent.grouphierarchy_data["tags"]:
                            self.agent.grouphierarchy_data["tags"][tag] = set()
                        self.agent.grouphierarchy_data["tags"][tag].add(last)

    class SearchGroup(CyclicBehaviour):
        async def on_start(self) -> None:
            self.logger = _logging.getLogger(self.__class__.__name__)
            self.logger.debug("starting behaviour")
            template = Template()
            template.set_metadata("resource", "searchgroup")
            self.set_template(template)

        async def run(self) -> None:
            msg = await self.receive(60)
            if msg:
                tags = json_loads(msg.get_metadata("tags"))
                groups = self.agent.grouphierarchy_data["tags"][tags[0]]
                for tag in tags[1:]:
                    groups.intersection(self.agent.grouphierarchy_data["tags"][tag])
                res = msg.make_reply()
                res.set_metadata("groups", groups)
                await self.send(res)

    class CreateGraph(CyclicBehaviour):
        async def on_start(self):
            self.logger = _logging.getLogger(self.__class__.__name__)
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
            self.logger = _logging.getLogger(self.__class__.__name__)
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

    def __init__(self, domain, verify_security, port):
        super().__init__(
            JID.fromstr("df@" + domain + "/admin"), verify_security=verify_security
        )
        self.port = port

    @classmethod
    def name(domain: str) -> str:
        return "df@" + domain + "/admin"

    async def setup(self):
        self.grouphierarchy_data = dict()
        self.dataanalysis_data = dict()
        self.group_tags = dict()

        self.add_behaviour(self.GroupHierarchy())
        self.add_behaviour(self.SearchGroup())
        self.add_behaviour(self.CreateGraph())
        self.add_behaviour(self.UpdateGraph())

        self.web.add_get("/groups", self.groups, template=None)
        self.web.add_get("/groups/refresh", self.refresh_groups, template=None)
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
        _logger.info("REST API running on port " + self.port)

    async def groups(self, request):
        graph = {
            "nodes": list(self.grouphierarchy_data["nodes"]),
            "links": list(self.grouphierarchy_data["links"]),
            "categories": list(self.grouphierarchy_data["categories"]),
            "node_members": self.grouphierarchy_data["node_members"],
        }
        return graph

    async def refresh_groups(self, request):
        pass

    async def dataanalysis(self, request):
        return self.dataanalysis_data
