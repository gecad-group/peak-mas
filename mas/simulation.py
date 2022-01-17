from abc import ABCMeta as _ABCMeta, abstractmethod
import asyncio as _asyncio
import logging as _logging

from mas import Agent, CyclicBehaviour, Template, PeriodicBehaviour, Message

_logger = _logging.getLogger('mas.Simulation')


class SyncAgent(Agent, metaclass=_ABCMeta):


    class _StepBehaviour(CyclicBehaviour):
        '''Listens for the Synchronizer messages.'''

        async def run(self):
            msg = await self.receive(10)
            if msg:
                if msg.get_metadata('sync') == 'step':
                    self.agent.period = int(msg.get_metadata('period'))
                    self.agent.iterate_properties()
                    await self.agent.step()
                if msg.get_metadata('sync') == 'stop':
                    self.kill()

        async def on_end(self):
            await self.agent.stop()


    def __init__(self, name: str, server: str, properties=None, verify_security=False):
        """Agent that listens to the Synchronizer.

        This is an abstract class. Step method must be overriden.

        Args:
            name (str): Name of the agent.
            server (str): Domain of the XMPP server to connect to.
            mas_name (str): Name of the MAS to be used to join a group chat between the agents.
            group_names (set[str], optional): Set of group names to join to. Defaults to {}.
            verify_security (bool, optional): Wether to verify or not the SSL certificates. Defaults to False.
        """
        super().__init__(name, server, properties, verify_security)
        self.period = 0
        template_step = Template()
        template_step.set_metadata('sync', 'step')
        template_stop = Template()
        template_stop.set_metadata('sync', 'stop')
        template = template_step | template_stop
        self.add_behaviour(self._StepBehaviour(), template)

    @abstractmethod
    async def step(self):
        """This method is executed at each step.

        It must be overriden.

        Raises:
            NotImplementedError: The step method must be overriden.
        """
        raise NotImplementedError('The step method must be overriden.')


class Synchronizer(Agent):

    class _StepBehaviour(PeriodicBehaviour):
        '''Sends a message to MAS group for each step.'''

        def __init__(self, group_jid, n_agents: int, periods: int, time_per_period:float, start_at=None):
            super().__init__(time_per_period, start_at=start_at)
            self.group_jid = group_jid
            self.n_agents = n_agents
            self.periods = periods

        async def on_start(self):
            while not len(self.agent.group_members(self.group_jid)) >= self.n_agents:
                await _asyncio.sleep(1)
            self.current_period = 0
            _logger.info('Starting simulation...')

        async def run(self):
            msg = Message()
            msg.to = self.group_jid
            if self.current_period >= self.periods:
                msg.set_metadata('sync', 'stop')
                self.kill()
            else:
                _logger.info('Period ' + str(self.current_period))
                msg.body = 'Period ' + str(self.current_period)
                msg.set_metadata('sync', 'step')
                msg.set_metadata('period', str(self.current_period))
            await self.send_to_group(msg)
            self.current_period += 1

        async def on_end(self):
            _logger.info('Ending simulation...')
            await _asyncio.sleep(5)
            await self.agent.stop()

    async def sync_group(self, jid, n_agents: int, time_per_period: float, periods: int):
        await self.join_group(jid)
        self.add_behaviour(self._StepBehaviour(jid, n_agents, periods, time_per_period))

        