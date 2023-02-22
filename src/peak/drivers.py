# Standard library imports
import logging
from abc import ABCMeta

# Third party imports
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import get_2comp

log = logging.getLogger("peak.mas.drivers")


class Driver(metaclass=ABCMeta):
    """Base interface for the Drivers."""

    pass


class DriverModBusTCP(Driver):
    """Protocol ModBus/TCP.

    Attributes:
        client: handles the ModBus/TCP comunication.
    """

    def __init__(self, host: str, unit_id: int = 1):
        """Inits Driver ModBus/TCP.

        Args:
            host: Hostname or IPv4/IPv6 address of the device.
            unit_id: Unit ID.
        """
        self.client = ModbusClient(host=host, unit_id=unit_id, auto_open=True)

    def read(self, register: int, unit_id: int = None) -> int:
        """Reads a given register of the device.

        Args:
            register: Register address (0 to 65535).
            unit_id: Unit ID.

        Returns:
            An integer that was read at the given register.
            Returns None if the value could not read from the
            target.
        """
        if unit_id is not None:
            self.client.unit_id = unit_id
        data = self.client.read_input_registers(reg_addr=register)
        if not data:
            log.warning(
                "%s cannot read from target %s.",
                self.__class__,
                self.client.host(),
                exc_info=self.client.last_except_txt(),
            )
            return None
        else:
            return get_2comp(data[0])

    def write(self, register: int, value: int, unit_id: int = None):
        """Writes a value in a given register.

        Args:
            register: Register address (0 to 65535).
            value: Value to be written.
            unit_id: Unit ID.
        """
        if unit_id is not None:
            self.client.unit_id = unit_id
        if not self.client.write_single_register(register, get_2comp(value)):
            log.warning(
                "%s cannot write to target %s.",
                self.__class__,
                self.client.host(),
                exc_info=self.client.last_except_txt(),
            )
            return False
        return True
