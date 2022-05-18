from abc import ABCMeta, abstractmethod
from typing import Dict
import itertools
from random import uniform
from pandas.core.frame import DataFrame

from peak.mas.drivers import Driver

class Property():

    def __init__(self, data, loop=False, random_range=None, offset = 0) -> None:
        self.data = data
        self.loop = loop
        self.offset = offset
        self.random_range = random_range
        self.iter = self._gen(data, loop, offset)
        self.current_value = next(self.iter)

    def _gen(self, data, loop, offset):
        f = True
        while f:
            try:
                data = data[offset:]
                for i in data:
                    if self.random_range:
                        yield i * uniform(1-self.random_range, 1+self.random_range)
                    else:
                        yield i

                if not loop:
                    while True: yield None
            except TypeError:
                f = False
        while True:
            yield data
    
    def next(self):
        self.current_value = next(self.iter)

    def __add__(self, other):
        if isinstance(other, Property):
            return self.current_value + other.current_value
        if isinstance(other, (float,int)):
            return self.current_value + other
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, Property):
            return float(self.current_value) - float(other.current_value)
        if isinstance(other, (float,int)):
            return self.current_value - other
        raise TypeError

    def __mul__(self, other):
        if isinstance(other, Property):
            return self.current_value * other.current_value
        if isinstance(other, (float,int)):
            return self.current_value * other
        raise TypeError

    def __div__(self, other):
        if isinstance(other, Property):
            return self.current_value / other.current_value
        if isinstance(other, (float,int)):
            return self.current_value / other
        raise TypeError

    def __repr__(self) -> str:
        return str(self.current_value)

    def __getitem__(self, item):
        return self.data[(item % len(self.data))-1]


class Properties(metaclass=ABCMeta):

    def __init__(self, full_name=None, name=None, number=None) -> None:
        self.agent_fullname: str = full_name
        self.agent_name:str = name
        self.agent_number:int = number
        self.ds = dict()
        self.build_dataset()

    def add_property(self, property_name, property: Property):
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        self.ds[self.agent_fullname][property_name] = property

    def add_dataset(self, dataframe: DataFrame, loop=False, random_range=None, offset = 0):
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        for property in dataframe:
            self.ds[self.agent_fullname][property] = Property(dataframe[property].to_list(), loop, random_range, offset)

    def add_driver(self, driver_name, driver: Driver):
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        self.ds[self.agent_fullname][driver_name] = driver

    @abstractmethod
    def build_dataset(self):
        pass
    
    def extract(self) -> Dict[str, Property]:
        return self.ds[self.agent_fullname]