from abc import ABCMeta
import logging

from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import get_2comp

log = logging.getLogger('peak.mas.drivers')

class Driver(metaclass=ABCMeta):
    
    def next(self):
        pass

class DriverModBusTCP(Driver):

    def __init__(self, host, unit_id = None) -> None:
        self.client = ModbusClient(host = host, unit_id=unit_id, auto_open=True)

    def read(self, register, unit_id=None):
        if unit_id is not None:
            self.client.unit_id(unit_id)
        data = self.client.read_input_registers(reg_addr=register)
        if not data:
            log.warning('%s cannot read from target %s.', self.__class__, self.client.host(), exc_info=self.client.last_except_txt())
        return get_2comp(data[0])

    def write(self, register, value, unit_id=None):
        if unit_id is not None:
            self.client.unit_id(unit_id)
        if not self.client.write_single_register(register, get_2comp(value)):
            log.warning('%s cannot write to target %s.', self.__class__, self.client.host(), exc_info=self.client.last_except_txt())