import asyncio
import logging as _logging

import mas

_logger = _logging.getLogger('mas.simulation')


class SyncAgent(mas.Agent):

    class StepBehaviour(mas.CyclicBehaviour):

        async def run(self):
            msg = await self.receive(10)
            if msg:
                if msg.get_metadata('sync') == 'step':
                    self.agent.step()
                if msg.get_metadata('sync') == 'stop':
                    await self.agent.stop()


    def __init__(self, name, server, mas_name, group_names: set[str] = {}, verify_security=False):
        super().__init__(name, server, mas_name, group_names, verify_security)
        template_step = mas.Template()
        template_step.set_metadata('sync', 'step')
        template_stop = mas.Template()
        template_stop.set_metadata('sync', 'stop')
        template = template_step | template_stop
        self.add_behaviour(self.StepBehaviour(), template)

    def step(self):
        raise NotImplementedError('The step method must be overriden')


class Synchronizer(mas.Agent):

    class WhatchMembersBehaviour(mas.PeriodicBehaviour):

        async def on_start(self):
            _logger.info('Waiting for agents to connect...')

        async def run(self):
            if len(self.agent.group_members(self.agent.mas_name)) > self.agent.n_agents:
                self.kill()

        async def on_end(self):
            _logger.info('Every agent is up and running!')
            self.agent.add_behaviour(self.agent.StepBehaviour(self.agent.time_per_period))

    class StepBehaviour(mas.PeriodicBehaviour):

        async def on_start(self):
            self.sim_period = 0
            _logger.info('Starting simulation...')

        async def run(self):
            self.sim_period += 1
            msg = mas.Message()
            if self.sim_period > self.agent.periods:
                msg.set_metadata('sync', 'stop')
                self.kill()
            else:
                _logger.info('Period ' + str(self.sim_period))
                msg.body = 'Period ' + str(self.sim_period)
                msg.set_metadata('sync', 'step')
                msg.set_metadata('period', str(self.sim_period))
            await self.send_to_group(msg)

        async def on_end(self):
            _logger.info('Ending simulation...')
            await asyncio.sleep(5)
            await self.agent.stop()

    NAME = 'synchronizer'

    def __init__(self, server, mas_name, n_agents, time_per_period, periods, verify_security=False):
        super().__init__(self.NAME, server, mas_name, verify_security=verify_security)
        self.n_agents = n_agents
        self.periods = periods
        self.time_per_period = time_per_period
        self.add_behaviour(self.WhatchMembersBehaviour(1))
        


