import asyncio as _asyncio

from peak import Message, PeriodicBehaviour


class PeriodicClock(PeriodicBehaviour):
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
        while not len(await self.agent.group_members(self.group_jid)) >= self.n_agents:
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
