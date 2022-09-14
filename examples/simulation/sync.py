from datetime import datetime, timedelta

import settings

from peak import Synchronizer


class sync(Synchronizer):
    async def setup(self) -> None:
        # n_agents = 3 --> agent + synchronizer + client
        await self.sync_group(
            settings.sync_group,
            3,
            datetime(2000, 1, 1),
            datetime(2000, 1, 2),
            timedelta(hours=1),
            0.5,
        )
