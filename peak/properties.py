from abc import ABCMeta, abstractmethod
from random import uniform
from typing import Dict, Iterable

from pandas import DataFrame

from peak.drivers import Driver


class Property:
    """Represents a property of an agent.

    Attributes:
        data: Array of objects.
        loop: If True, when the property reaches the end of the data array
            it comes back to the begining.
        offset: Offset of the index of the data array.
        random_range: Percentage that applies randomness to the data.
        current_value: Current value of the property.
    """

    def __init__(self, data: Iterable, loop:bool=False, random_range: float=None, offset: int=0):
        self.data = data
        self.loop = loop
        self.offset = offset
        self.random_range = random_range
        self.iter = self._gen(data, loop, offset)
        self.current_value = next(self.iter)

    def _gen(self, data: Iterable, loop:bool, offset: int):
        """Retrieves values from the data iteratively.

        Args:
            data: Array of objects.
            loop: If True, when the property reaches the end of the data array
                it comes back to the begining.
            offset: Offset of the index of the data array.

        Yields:
            The next value in the data array.
        """
        f = True
        while f:
            try:
                data = data[offset:]
                for i in data:
                    if self.random_range:
                        yield i * uniform(1 - self.random_range, 1 + self.random_range)
                    else:
                        yield i

                if not loop:
                    while True:
                        yield None
            except TypeError:
                f = False
        while True:
            yield data

    def next(self):
        """Iterates the data array.
        """
        self.current_value = next(self.iter)

    def __add__(self, other):
        if isinstance(other, Property):
            return self.current_value + other.current_value
        if isinstance(other, (float, int)):
            return self.current_value + other
        raise TypeError

    def __sub__(self, other):
        if isinstance(other, Property):
            return float(self.current_value) - float(other.current_value)
        if isinstance(other, (float, int)):
            return self.current_value - other
        raise TypeError

    def __mul__(self, other):
        if isinstance(other, Property):
            return self.current_value * other.current_value
        if isinstance(other, (float, int)):
            return self.current_value * other
        raise TypeError

    def __div__(self, other):
        if isinstance(other, Property):
            return self.current_value / other.current_value
        if isinstance(other, (float, int)):
            return self.current_value / other
        raise TypeError

    def __repr__(self) -> str:
        return str(self.current_value)

    def __getitem__(self, item):
        return self.data[(item % len(self.data)) - 1]


class Properties(metaclass=ABCMeta):
    """Used to filtrate and process the data to be injected in the agent.

    Attributes:
        agent_fullname: If the agent is a clone the full name will have 
            its original name the the clone number. If its not, the full
            name will be equal to the name.
        agent_name: Just the name without the clone number.
        agent_number: The clone number if its a clone.
    """
    def __init__(self, full_name: str=None, name: str=None, number: int=None) -> None:
        self.agent_fullname: str = full_name
        self.agent_name: str = name
        self.agent_number: int = number
        self.ds = dict()
        self.build_dataset()

    def add_property(self, property_name: str, property: Property):
        """Adds a single Property to the agent's properties. 

        Args:
            property_name: Name of the property.
            property: An instance of Property.
        """
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        self.ds[self.agent_fullname][property_name] = property

    def add_dataset(
        self, dataframe: DataFrame, loop: bool=False, random_range: float=None, offset: int=0
    ):
        """Adds a dataframe to the agent's properties.

        Args:
            dataframe: Pandas Dataframe.
            loop: If True, when the property reaches the end of the data array
                it comes back to the begining.
            random_range: Percentage that applies randomness to the data.
            offset: Offset of the index of the data array.
        """
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        for property in dataframe:
            self.ds[self.agent_fullname][property] = Property(
                dataframe[property].to_list(), loop, random_range, offset
            )

    def add_driver(self, driver_name: str, driver: Driver):
        """Adds a driver to the agent properties.

        Args:
            driver_name: Name of the driver.
            driver: The actual driver.
        """
        if self.agent_fullname not in self.ds:
            self.ds[self.agent_fullname] = dict()
        self.ds[self.agent_fullname][driver_name] = driver

    @abstractmethod
    def build_dataset(self):
        """Contains the process of filtering and adding the data to the agent.
        """
        pass

    def extract(self) -> Dict[str, Property]:
        """Extracts the dataset from this properties.

        Returns:
            A dictionary with the agents properties.
        """
        return self.ds[self.agent_fullname]
