import asyncio as _asyncio
import json
import logging as _logging
from abc import ABCMeta as _ABCMeta
from abc import abstractmethod
from datetime import datetime, timedelta

import aiohttp_cors
from aioxmpp import JID

from peak import Agent, CyclicBehaviour, Message, PeriodicBehaviour, Template

_logger = _logging.getLogger(__name__)


class SyncAgent(Agent, metaclass=_ABCMeta):
    """Is synchronized by the Synchronizer.

    Every agent that needs to be synchronized needs
    to extend this class.
    """

    class _StepBehaviour(CyclicBehaviour):
        async def on_start(self):
            self.logger.info("Waiting for simulation to start...")

        async def run(self):
            msg = await self.receive(10)
            if msg:
                if msg.get_metadata("sync") == "step":
                    period = int(msg.get_metadata("period"))
                    time = None
                    if msg.get_metadata("time"):
                        time = datetime.strptime(
                            msg.get_metadata("time"), "%Y-%m-%d %H:%M:%S"
                        )
                    await self.agent.step(period, time)
                    self.logger.info(msg.body)
                if msg.get_metadata("sync") == "stop":
                    self.logger.info("Simulation ended.")
                    self.kill()

        async def on_end(self):
            await self.agent.stop()

    def __init__(self, jid: JID, verify_security: bool = False):
        """Inits the SyncAgent with the JID provided.

        Args:
            jid (:obj:`JID`): Agent's XMPP identifier.
            verify_security (bool, optional): If True, verifies the SSL certificates.
                Defaults to False.
        """
        super().__init__(jid, verify_security)
        template_step = Template()
        template_step.set_metadata("sync", "step")
        template_stop = Template()
        template_stop.set_metadata("sync", "stop")
        template = template_step | template_stop
        self.add_behaviour(self._StepBehaviour(), template)

    @abstractmethod
    async def step(self, period: int, time: datetime = None):
        """Executed at each tick of the Synchronizer clock.

        To be implemented by the user.

        Args:
            period (int): Number of the current period.
            time (datetime, optional): Current datetime inside the simulation. It must be
                configured in the Synchronizer."""
        raise NotImplementedError()


class Synchronizer(Agent):
    """Synchronizes the syncagents.

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
            self.logger.info("Waiting for all agents to enter the group...")
            while (
                not len(await self.agent.group_members(self.group_jid)) >= self.n_agents
            ):
                await _asyncio.sleep(1)
            self.current_period = 0
            self.logger.info("Starting simulation...")

        async def run(self):
            msg = Message()
            msg.to = self.group_jid
            if self.current_period >= self.periods:
                msg.set_metadata("sync", "stop")
                self.kill()
            else:
                self.logger.info(f"Period {self.current_period}")
                msg.body = f"Period {self.current_period}"
                msg.set_metadata("sync", "step")
                msg.set_metadata("period", str(self.current_period))
            await self.send_to_group(msg)
            self.current_period += 1

        async def on_end(self):
            self.logger.info("Ending simulation...")
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
            self.logger.info("Waiting for all agents to enter the group...")
            while (
                not len(await self.agent.group_members(self.group_jid)) >= self.n_agents
            ):
                await _asyncio.sleep(1)
            self.current_period = 0
            self.logger.info("Starting simulation...")

        async def run(self):
            msg = Message()
            msg.to = self.group_jid
            if self.time >= self.end_time:
                msg.set_metadata("sync", "stop")
                self.kill()
            else:
                self.logger.info(f"Period {self.current_period} ({self.time})")
                msg.body = f"Period {self.current_period} ({self.time})"
                msg.set_metadata("sync", "step")
                msg.set_metadata("period", str(self.current_period))
                msg.set_metadata(
                    "time", datetime.strftime(self.time, "%Y-%m-%d %H:%M:%S")
                )
            await self.send_to_group(msg)
            self.current_period += 1
            self.time += self.period_time

        async def on_end(self):
            self.logger.info("Ending simulation...")
            await self.agent.stop()

    async def sync_group_period(
        self, group_jid: str, n_agents: int, interval: float, periods: int
    ):
        """Synchronizes a group of agents.

        The clock is based on the number of the current period.

        Args:
            group_jid: Identifier of the XMPP group to be synchronized.
            n_agents: Number of agents to be synchronized. Synchronizer
                awaits for this number of agents to join the group before
                it starts the simulation.
            interval: Time in seconds between each period.
            periods: Number of periods to simulate.
        """
        await self.join_group(group_jid)
        self.add_behaviour(self._PeriodicClock(group_jid, n_agents, periods, interval))

    async def sync_group_time(
        self,
        group_jid: str,
        n_agents: int,
        initial_datetime: datetime,
        end_datetime: datetime,
        internal_interval: timedelta,
        external_period_time: float,
        start_at: datetime = None,
    ):
        """Synchronizes a group of agents.

        Here two time dimensions are created. One is the real-time at which
        the clock of the Synchronizer will run. The other is the fictional
        datetime created inside the simulation. For example, one second
        can correspond to one day inside the simulation.

        Args:
            group_jid: Identifier of the XMPP group to be synchronized.
            n_agents: Number of agents to be synchronized. Synchronizer
                awaits for this number of agents to join the group before
                it starts the simulation.
            initial_datetime: Defines the initial date and time inside the
                simulation.
            end_datetime: Defines the date and time at which the simulation ends.
            internal_interval: Time between each period relative to the initial and
                end datetimes.
            interval: Time in seconds between each period relative to the Synchronizers
                clock.
            start_at: Schedules the simulation to start at a given time. If None the
                simulation starts right away.
        """
        await self.join_group(group_jid)
        self.add_behaviour(
            self._DateTimeClock(
                group_jid,
                n_agents,
                initial_datetime,
                end_datetime,
                internal_interval,
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

    class _EcosystemHierarchy(CyclicBehaviour):
        """Manages the group structure of all the multi-agent systems."""

        async def on_start(self):
            self.logger = self.agent.logger.getChild(self.__class__.__name__)
            self.logger.debug("starting behaviour")
            template = Template()
            template.set_metadata("resource", "treehierarchy")
            self.set_template(template)

        async def run(self):
            msg = await self.receive(60)
            if msg:
                self.logger.debug("message received")
                path = msg.get_metadata("path")
                domain = msg.get_metadata("domain")
                if meta_tags := msg.get_metadata("tags"):
                    tags = json.loads(meta_tags)
                nodes = path.split("/")
                self.logger.debug("nodes: " + str(nodes))
                level = "level"

                if (
                    msg.get_metadata("leave")
                    and msg.sender
                    in self.agent.ecosystemhierarchy_data["node_members"][nodes[-1]]
                ):
                    self.logger.debug(str(msg.sender) + " leaving " + path)
                    self.agent.ecosystemhierarchy_data["node_members"][
                        nodes[-1]
                    ].remove(msg.sender)
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
                    self.logger.debug(str(msg.sender) + " entering " + path)
                    last = None
                    for i, node in enumerate(nodes):
                        self.agent.ecosystemhierarchy_data["nodes"].add(
                            (node, level + str(i), domain)
                        )
                        if (
                            node
                            not in self.agent.ecosystemhierarchy_data["node_members"]
                        ):
                            self.agent.ecosystemhierarchy_data["node_members"][
                                node
                            ] = []
                        self.agent.ecosystemhierarchy_data["categories"].add(
                            level + str(i)
                        )
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

    class _SearchCommunity(CyclicBehaviour):
        """Handles all the requests to search for groups."""

        async def on_start(self) -> None:
            self.logger = self.agent.logger.getChild(self.__class__.__name__)
            self.logger.debug("starting behaviour")
            template = Template()
            template.set_metadata("resource", "searchgroup")
            self.set_template(template)

        async def run(self) -> None:
            msg = await self.receive(60)
            if msg and (meta_tags := msg.get_metadata("tags")):
                tags = json.loads(meta_tags)
                communities: set = self.agent.ecosystemhierarchy_data["tags"][tags[0]]
                for tag in tags[1:]:
                    communities = communities.intersection(
                        self.agent.ecosystemhierarchy_data["tags"][tag]
                    )
                res = msg.make_reply()
                res.set_metadata("communities", json.dumps(list(communities)))
                await self.send(res)

    class _CreateGraph(CyclicBehaviour):
        """Handles the requests to create graphs"""

        async def on_start(self):
            self.logger = self.agent.logger.getChild(self.__class__.__name__)
            self.logger.debug("starting behaviour")
            template = Template()
            template.set_metadata("resource", "graph")
            template.set_metadata("action", "create")
            self.set_template(template)

        async def run(self) -> None:
            msg = await self.receive(60)
            if msg:
                self.logger.debug(msg)
                id = msg.get_metadata("id")
                graph = json.loads(msg.get_metadata("graph"))
                self.agent.dataanalysis_data[id] = graph

    def __init__(self, domain, verify_security, port):
        super().__init__(
            JID.fromstr("df@" + domain + "/admin"), verify_security=verify_security
        )
        self.port = port
        self.logger = _logger.getChild(self.__class__.__name__)

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

        self.add_behaviour(self._EcosystemHierarchy())
        self.add_behaviour(self._SearchCommunity())
        self.add_behaviour(self._CreateGraph())

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
