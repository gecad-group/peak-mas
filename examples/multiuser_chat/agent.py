from peak.mas import Agent, JoinGroup
import logging

class agent(Agent):

    async def setup(self) -> None:
        self.add_behaviour(JoinGroup('group1', 'conference.localhost', ['test', 'awesome', 'cool']))
        self.add_behaviour(JoinGroup('group2', 'conference.localhost', ['test', 'awesome']))
        self.add_behaviour(JoinGroup('group3', 'conference.localhost', ['test',]))