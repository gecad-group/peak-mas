from abc import ABCMeta as _ABCMeta, abstractmethod
import asyncio as _asyncio
import logging as _logging

import mas

_logger = _logging.getLogger('mas.simulation')


class SyncAgent(mas.Agent, metaclass=_ABCMeta):


    class _StepBehaviour(mas.CyclicBehaviour):
        '''Listens for the Synchronizer messages.'''

        async def run(self):
            msg = await self.receive(10)
            if msg:
                if msg.get_metadata('sync') == 'step':
                    self.agent.step()
                if msg.get_metadata('sync') == 'stop':
                    await self.agent.stop()


    def __init__(self, name: str, server: str, mas_name: str, group_names: set[str] = {}, verify_security=False):
        """Agent that listens to the Synchronizer.

        This is an abstract class. Step method must be overriden.

        Args:
            name (str): Name of the agent.
            server (str): Domain of the XMPP server to connect to.
            mas_name (str): Name of the MAS to be used to join a group chat between the agents.
            group_names (set[str], optional): Set of group names to join to. Defaults to {}.
            verify_security (bool, optional): Wether to verify or not the SSL certificates. Defaults to False.
        """
        super().__init__(name, server, mas_name, group_names, verify_security)
        template_step = mas.Template()
        template_step.set_metadata('sync', 'step')
        template_stop = mas.Template()
        template_stop.set_metadata('sync', 'stop')
        template = template_step | template_stop
        self.add_behaviour(self._StepBehaviour(), template)

    @abstractmethod
    def step(self):
        """This method is executed at each step.

        It must be overriden.

        Raises:
            NotImplementedError: The step method must be overriden.
        """
        raise NotImplementedError('The step method must be overriden.')


class Synchronizer(mas.Agent):

    class _WaitForMembersBehaviour(mas.PeriodicBehaviour):
        '''Checks if all the expected agents are in the MAS group.
        
        Starts the simulation after all agents are connected to the group.'''

        async def on_start(self):
            _logger.info('Waiting for agents to connect...')

        async def run(self):
            if len(self.agent.group_members(self.agent.mas_name)) > self.agent.n_agents:
                self.kill()

        async def on_end(self):
            _logger.info('Every agent is up and running!')
            self.agent.add_behaviour(self.agent._StepBehaviour(self.agent.time_per_period))

    class _StepBehaviour(mas.PeriodicBehaviour):
        '''Sends a message to MAS group for each step.'''

        async def on_start(self):
            self.current_period = 0
            _logger.info('Starting simulation...')

        async def run(self):
            self.current_period += 1
            msg = mas.Message()
            if self.current_period > self.agent.periods:
                msg.set_metadata('sync', 'stop')
                self.kill()
            else:
                _logger.info('Period ' + str(self.current_period))
                msg.body = 'Period ' + str(self.current_period)
                msg.set_metadata('sync', 'step')
                msg.set_metadata('period', str(self.current_period))
            await self.send_to_group(msg)

        async def on_end(self):
            _logger.info('Ending simulation...')
            await _asyncio.sleep(5)
            await self.agent.stop()

    NAME = 'synchronizer'

    def __init__(self, server: str, mas_name: str, n_agents: int, time_per_period: float, periods: int, verify_security=False):
        """Agent responsible for synchronizing the simulation.

        Args:
            server (str): Domain of the XMPP server to connect to.
            mas_name (str): Name of the MAS to be used to create a group chat between the agents.
            n_agents (int): Number of agents expected to connect.
            time_per_period (float): Duration of each period.
            periods (int): Number of total periods to simulate.
            verify_security (bool, optional): Wether to verify or not the SSL certificates. Defaults to False.
        """
        super().__init__(self.NAME, server, mas_name, verify_security=verify_security)
        self.n_agents = n_agents
        self.periods = periods
        self.time_per_period = time_per_period
        self.add_behaviour(self._WaitForMembersBehaviour(1))
        
if __name__ == '__main__':
    SyncAgent('', '', '')