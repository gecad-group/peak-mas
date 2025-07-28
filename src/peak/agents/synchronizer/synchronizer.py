from datetime import datetime, timedelta

from peak import Agent
from peak.agents.synchronizer.behaviors import DateTimeClock, PeriodicClock


class Synchronizer(Agent):
    """Synchronizes the syncagents.

    The Synchronizer creates a group of agents, awaits for
    the agents to join the group and starts the clock of the
    simulation.
    """

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
        self.add_behaviour(PeriodicClock(group_jid, n_agents, periods, interval))

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
            DateTimeClock(
                group_jid,
                n_agents,
                initial_datetime,
                end_datetime,
                internal_interval,
                external_period_time,
                start_at,
            )
        )
