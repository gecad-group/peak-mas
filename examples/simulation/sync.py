# Standard library imports
from datetime import datetime, timedelta

# Third party imports
import settings

# Reader imports
from peak import Synchronizer


class sync(Synchronizer):
    async def setup(self) -> None:
        # n_agents = 3 --> agent + synchronizer + client
        await self.sync_group_time(
            settings.sync_group,
            2,
            datetime(2000, 1, 1),
            datetime(2000, 1, 2),
            timedelta(hours=1),
            0.5,
        )
