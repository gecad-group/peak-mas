import logging
import peak.mas as peak
from peak.management.df.df import df_name
from json import dumps as json_dumps


class CreateNode(peak.OneShotBehaviour):

    def __init__(self, node: str, affiliation: str = None):
        super().__init__()
        self.affiliation = affiliation
        self.node = node
    
    async def on_start(self):
        self.template = peak.Template()
        self.template.set_metadata('resource', 'pubsub_create_node')

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata('resource', 'pubsub_create_node')
        msg.set_metadata('affiliation', self.affiliation if self.affiliation else '')
        msg.set_metadata('node_jid', self.node)
        await self.send(msg)
        res = await self.receive(60)
        if res:
            logger = logging.getLogger('CreateNode')
            logger.info('PubSub node ' + self.node + ' created')

class JoinGroup(peak.OneShotBehaviour):

    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata('resource', 'treehierarchy')
        msg.set_metadata('path', self.path)
        msg.set_metadata('domain', self.domain)
        await self.send(msg)
        nodes = self.path.split('/')
        for node in nodes[:-1]:
            await self.agent.join_group(node + '_down@' + self.domain)
        await self.agent.join_group(nodes[-1] + '@' + self.domain)
        await self.agent.join_group(nodes[-1] + '_down@' + self.domain)

class LeaveGroup(peak.OneShotBehaviour):

    def __init__(self, path: str, domain: str):
        super().__init__()
        self.path = path
        self.domain = domain

    async def run(self):
        msg = peak.Message()
        msg.to = df_name(self.agent.jid.domain)
        msg.set_metadata('resource', 'treehierarchy')
        msg.set_metadata('path', self.path)
        msg.set_metadata('domain', self.domain)
        msg.set_metadata('leave', 'true')
        await self.send(msg)
        nodes = self.path.split('/')
        for node in nodes[:-1]:
            await self.agent.leave_group(node + '_down@' + self.domain)
        await self.agent.leave_group(nodes[-1] + '@' + self.domain)
        await self.agent.leave_group(nodes[-1] + '_down@' + self.domain)

class ExportDataToFile(peak.OneShotBehaviour):

    def __init__(self, file_name: str, properties: list, interval: int = None):
        self.interval = interval
        self.file_name = file_name
        self.properties = properties

    async def run(self) -> None:
        if isinstance(self.agent, peak.SyncAgent):
            self.agent.add_behaviour(_ExportDataToFileSync(self.file_name, self.properties))
        else:
            self.agent.add_behaviour(_ExportDataToFile(self.interval, self.file_name, self.properties))

class ExportDataToGraph(peak.OneShotBehaviour):

    def __init__(self, graph_name: str, properties: list, interval: int = None, graph_options: str = ''):
        self.interval = interval
        self.graph_name = graph_name
        self.properties = properties
        self.graph_options = graph_options

    async def run(self) -> None:
        if isinstance(self.agent, peak.SyncAgent):
            self.agent.add_behaviour(_ExportDataToDFSync(self.graph_name, self.properties, self.graph_options))
        else:
            self.agent.add_behaviour(_ExportDataToDF(self.interval, self.graph_name, self.properties, self.graph_options))

class _ExportDataToFile(peak.PeriodicBehaviour):

    def __init__(self, interval: int, file_name: str, properties: list):
        super().__init__(interval, None)
        self.file_name = file_name
        self. data = {}
        for property in properties:
            self.data[property] = []

    async def run(self) -> None:
        for property in self.data:
            attribute = getattr(self.agent, property)
            if type(attribute) is peak.Property:
                self.data[property].append(attribute.current_value)
            else:
                self.data[property].append(attribute)

    async def on_end(self) -> None:
        with open(self.file_name, 'w') as f:
            f.write(json_dumps(self.data))

class _ExportDataToDF(peak.PeriodicBehaviour):

    def __init__(self, interval: int, graph_name: str, properties: list, graph_options = ''):
        super().__init__(interval, None)
        self.graph_name = graph_name
        self.graph_options = graph_options
        self. data = {}
        for property in properties:
            self.data[property] = []

    async def on_start(self) -> None:
        msg = peak.Message(to=df_name(self.agent.jid.domain))
        msg.body = json_dumps(self.data)
        msg.metadata = {
            'graph_name': self.graph_name,
            'graph_options': self.graph_options,
            'resource': 'dataanalysis'
        }
        self.send(msg)

    async def run(self) -> None:
        for property in self.data:
            attribute = getattr(self.agent, property)
            if type(attribute) is peak.Property:
                self.data[property].append(attribute.current_value)
            else:
                self.data[property].append(attribute)
        msg = peak.Message(to=df_name(self.agent.jid.domain))
        msg.body = json_dumps(self.data)
        msg.metadata = {
            'graph_name': self.graph_name,
            'graph_options': self.graph_options,
            'resource': 'dataanalysis'
        }
        self.send(msg)

class _ExportDataToFileSync(peak.CyclicBehaviour):

    def __init__(self, file_name: str, properties: list):
        super().__init__()
        self.file_name = file_name
        self. data = {}
        for property in properties:
            self.data[property] = []

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg:
            if msg.get_metadata('sync') == 'step':
                for property in self.data:
                    attribute = getattr(self.agent, property)
                    if type(attribute) is peak.Property:
                        self.data[property].append(attribute.current_value)
                    else:
                        self.data[property].append(attribute)
            if msg.get_metadata('sync') == 'stop':
                with open(self.file_name, 'w') as f:
                    f.write(json_dumps(self.data))
        
class _ExportDataToDFSync(peak.CyclicBehaviour):

    def __init__(self, graph_name: str, properties: list, graph_options = ''):
        super().__init__()
        self.graph_name = graph_name
        self.graph_options = graph_options
        self. data = {}
        for property in properties:
            self.data[property] = []

    async def on_start(self) -> None:
        msg = peak.Message(to=df_name(self.agent.jid.domain))
        msg.body = json_dumps(self.data)
        msg.metadata = {
            'graph_name': self.graph_name,
            'graph_options': self.graph_options,
            'resource': 'dataanalysis'
        }
        self.send(msg)

    async def run(self) -> None:
        msg = await self.receive(60)
        if msg and msg.get_metadata('sync') == 'step':
            for property in self.data:
                attribute = getattr(self.agent, property)
                if type(attribute) is peak.Property:
                    self.data[property].append(attribute.current_value)
                else:
                    self.data[property].append(attribute)
            msg = peak.Message(to=df_name(self.agent.jid.domain))
            msg.body = json_dumps(self.data)
            msg.metadata = {
                'graph_name': self.graph_name,
                'graph_options': self.graph_options,
                'resource': 'dataanalysis'
            }
            self.send(msg)
   

    




