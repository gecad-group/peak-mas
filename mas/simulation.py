import spade
import spade.agent
import spade.behaviour
import spade.message

import mas.base as base


class SyncAgent(base.MASAgent):

    class StopAgent(spade.behaviour.OneShotBehaviour):

        async def run(self):
            await self.agent.stop()
    
    def __init__(self, name, server, mas_name, player_types: set[str], verify_security=False):
        super().__init__(name, server, mas_name, player_types, verify_security)
        self.period = 0
        template_step = spade.template.Template()
        template_step.set_metadata('sync', 'step')
        template_stop = spade.template.Template()
        template_stop.set_metadata('sync', 'stop')
        self.set_message_handler(template_step, self._step_handler)
        self.set_message_handler(template_stop, self._stop_handler)

    def _stop_handler(self, sender, message):
        self.add_behaviour(self.StopAgent())

    def _step_handler(self, sender, message):
        self.step()

    def step(self):
        raise NotImplementedError('The step method must be overriden')


class Synchronizer(base.MASAgent):

    class WhatchMembersBehaviour(spade.behaviour.PeriodicBehaviour):

        async def on_start(self):
            print('Waiting for agents to connect...')

        async def run(self):
            if len(self.agent.room_members(self.agent.mas_name)) > self.agent.n_agents:
                self.kill()

        async def on_end(self):
            print('Every agent is up and running!')
            self.agent.add_behaviour(self.agent.StepBehaviour(self.agent.time()))

    class StepBehaviour(spade.behaviour.PeriodicBehaviour):

        async def on_start(self):
            self.sim_period = 0
            print('Starting simulation...')

        async def run(self):
            self.sim_period += 1
            msg = spade.message.Message()
            if self.sim_period > self.agent.periods:
                msg.set_metadata('sync', 'stop')
                self.kill()
            else:
                print('Period ' + str(self.sim_period))
                msg.set_metadata('sync', 'step')
            msg.set_metadata('period', str(self.sim_period))
            request =  self.agent.request(msg, leave=False)
            await request.join()

        async def on_end(self):
            print('Ending simulation...')
            await self.agent.stop()

    NAME = 'Synchronizer'

    def __init__(self, server, mas_name, n_agents, clock, periods, granularity, speed = None, verify_security=False):
        super().__init__(self.NAME, server, mas_name, {self.NAME.lower()}, verify_security)
        self.n_agents = n_agents
        self.subs = set()
        self.clock = clock
        self.periods = periods
        self.granularity = granularity
        self.speed = speed

    def time(self):
        return 0.2 #fazer os calculos da velocidade aqui

    async def setup(self):
        self.add_behaviour(self.WhatchMembersBehaviour(1))


