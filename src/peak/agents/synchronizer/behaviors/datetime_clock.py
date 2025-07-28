import asyncio as _asyncio
from datetime import datetime, timedelta

from peak import Message, PeriodicBehaviour


class DateTimeClock(PeriodicBehaviour):
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
        while not len(await self.agent.group_members(self.group_jid)) >= self.n_agents:
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
            msg.set_metadata("time", datetime.strftime(self.time, "%Y-%m-%d %H:%M:%S"))
        await self.send_to_group(msg)
        self.current_period += 1
        self.time += self.period_time

    async def on_end(self):
        self.logger.info("Ending simulation...")
        await self.agent.stop()
