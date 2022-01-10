from abc import ABCMeta, abstractmethod

from pandas.core.frame import DataFrame

from mas.drivers import Driver

class Property:

    def __init__(self, value, loop=False) -> None:
        self.value = self._gen(value, loop)

    
    def _gen(self, value, loop):
        f = True
        while f:
            try:
                for i in value:
                    yield i
                if not loop:
                    while True: yield None
            except TypeError:
                f = False
        while True:
            yield value
    
    def __repr__(self) -> str:
        return str(next(self.value))

    #def __getitem__(self, item):
    #    return next(itertools.islice(self.value, item, None))

class Properties(metaclass=ABCMeta):

    def __init__(self, name=None) -> None:
        self.agent_name = name
        self.ds = dict()
        self.build_dataset()

    def add_property(self, agent_name, property_name, property: Property):
        self.ds[agent_name][property_name] = property

    def add_dataset(self, agent_name, dataframe: DataFrame):
        self.ds[agent_name] = dict()
        for property in dataframe:
            self.ds[agent_name][property] = Property(dataframe[property].to_list())

    def add_driver(self, agent_name, driver: Driver):
        self.ds[agent_name] = dict()
        for property in driver:
            self.ds[agent_name][property] = driver[property]

    @abstractmethod
    def build_dataset(self):
        pass
    
    def extract(self, name) -> dict[Property]:
        return self.ds[name]

if __name__ == '__main__':
    p = Property([1,2,3,4,5,6,7,8], loop=True)
    #for _ in range(10):
    #    print(p)
    print(p[9])
    print(p)
    print(p[9])