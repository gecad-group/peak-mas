import asyncio as _asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from abc import abstractmethod
from datetime import datetime, timedelta

from aioxmpp import JID

from peak.mas import (Agent, CyclicBehaviour, Message, PeriodicBehaviour,
                      Template)

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
