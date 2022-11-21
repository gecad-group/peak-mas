# Standard library imports
import asyncio as _asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from abc import abstractmethod
from datetime import datetime, timedelta
from json import loads as json_loads

# Third party imports
import aiohttp_cors
from aioxmpp import JID

# Reader imports
from peak import Agent, CyclicBehaviour, Message, PeriodicBehaviour, Template
from peak.properties import Properties

_logger = _logging.getLogger(__name__)


class SyncAgent(Agent, metaclass=_ABCMeta):
    """Agent that is synchronized by the Synchronizer.

    Every agent that needs to be synchronized needs
    to extend this class.

    Attributes:
        period: An integer representing the number of the period inside the simulation.
        time: A datetime of the current moment in the simmulation.
    """

    class _StepBehaviour(CyclicBehaviour):
        """Listens for the Synchronizer's clock's ticks."""

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

    def __init__(
        self, jid: JID, properties: Properties = None, verify_security: bool = False
    ):
        """Agent that listens to the Synchronizer.

        Args:
            jid: XMPP identifier of the agent.
            properties: Atributes of the agent to be injected.
            verify_security: If True verifies SSL certificates.
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
        """Executed at each tick of the Synchronizer clock.

        To be implemented by the user."""
        raise NotImplementedError()


class Synchronizer(Agent):
    """Agent that synchronizes the other agents.

    The Synchronizer creates a group of agents, awaits for
    the agents to join the group and starts the clock of the
    simulation.
    """

    class _PeriodicClock(PeriodicBehaviour):
        """Handles the clock of the simulation.

        This clock tracks the number of the current period
        throughout the simulation.
        """

        def __init__(
            self,
            group_jid: str,
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

    class _DateTimeClock(PeriodicBehaviour):
        """Handles the clock of the simulation.

        This clock tracks the current date and time of the
        simulation throughout its execution.
        """

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

    async def sync_group_period(
        self, group_jid: str, n_agents: int, time_per_period: float, periods: int
    ):
        """Synchronizes a group of agents.

        The clock is based on the number of the current period.

        Args:
            group_jid: Identifier of the XMPP group to be synchronized.
            n_agents: Number of agents to be synchronized. Synchronizer
                awaits for this number of agents to join the group before
                it starts the simulation.
            time_per_period: time in seconds between each period.
            periods: number of periods to simulate.
        """
        await self.join_group(group_jid)
        self.add_behaviour(
            self._PeriodicClock(group_jid, n_agents, periods, time_per_period)
        )

    async def sync_group_time(
        self,
        group_jid: str,
        n_agents: int,
        initial_time: datetime,
        end_time: datetime,
        internal_period_time: timedelta,
        external_period_time: float,
        start_at: datetime = None,
    ):
        """Synchronizes a group of agents.

        The clock is based on the date and time inside of the simulation.

        Args:
            group_jid: Identifier of the XMPP group to be synchronized.
            n_agents: Number of agents to be synchronized. Synchronizer
                awaits for this number of agents to join the group before
                it starts the simulation.
            initial_time: defines the internal date and time at the start of the
                simulation.
            end_time: defines the internal date and time at which the simulation ends.
            internal_period_time: time between each period inside the simulation.
            period_time_real: time between each tick of the clock.
            start_at: schedules the simulation start at a given time. If None the
                simulation starts right away.
        """
        await self.join_group(group_jid)
        self.add_behaviour(
            self._DateTimeClock(
                group_jid,
                n_agents,
                initial_time,
                end_time,
                internal_period_time,
                external_period_time,
                start_at,
            )
        )


class DF(Agent):
    """Directory Facilitator.

    This agent makes available the data that it gathers from multi-agent systems
    publicly through a REST API. It also provides a Yellow Page Service to the
    agents.
    """

    class _GroupHierarchy(CyclicBehaviour):
        """Manages the group structure of all the multi-agent systems."""

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
                if meta_tags := msg.get_metadata("tags"):
                    tags = json_loads(meta_tags)
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
                            for source, _, _ in self.agent.grouphierarchy_data["links"]
                        ):
                            self.agent.grouphierarchy_data["node_members"].pop(
                                node
                            )  # this line can be removed, there is no need in removing the node from the dict
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
                        self.agent.grouphierarchy_data["nodes"].add(
                            (node, level + str(i), domain)
                        )
                        if node not in self.agent.grouphierarchy_data["node_members"]:
                            self.agent.grouphierarchy_data["node_members"][node] = []
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
                                        + 1,  # this plus one is for the dashboard to not draw empty nodes (size of the node)
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

    class _SearchGroup(CyclicBehaviour):
        """Handles all the requests to search for groups."""

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

    class _CreateGraph(CyclicBehaviour):
        """Handles the requests to create graphs"""

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

    class _UpdateGraph(CyclicBehaviour):
        """Handles the requests to update the data of a given graph."""

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
    def name(cls, domain: str) -> str:
        """Retrieves the JID of the DF based on the agent domain.

        Args:
            domain: server's name

        Returns:
            The string of the complete JID of the DF.
        """
        return "df@" + domain + "/admin"

    async def setup(self):
        self.grouphierarchy_data = dict()
        self.dataanalysis_data = dict()
        self.group_tags = dict()

        self.add_behaviour(self._GroupHierarchy())
        self.add_behaviour(self._SearchGroup())
        self.add_behaviour(self._CreateGraph())
        self.add_behaviour(self._UpdateGraph())

        # Creates routes.
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
