from datetime import datetime

from peak import CyclicBehaviour


class StepBehaviour(CyclicBehaviour):
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
