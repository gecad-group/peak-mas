from typing import Type

from spade.template import Template as _Template

from peak.logging import getLogger
from peak.message import MessageBase

logger = getLogger(__name__)


class Template(MessageBase, _Template):
    """PEAK's template for matching messages."""

    def set_metadata(self, key: str, value: str = None) -> None:
        """
        Add a new metadata to the message

        Args:
          key (str): name of the metadata
          value (str): value of the metadata

        """
        if not isinstance(key, str):
            raise TypeError("'key' of metadata MUST be string")
        if value is not None and not isinstance(value, str):
            raise TypeError("'value' of metadata MUST be string or None")
        self.metadata[key] = value

    def match(self, message: Type["MessageBase"]) -> bool:
        """
        Returns wether a message matches with this message or not.
        The message can be a Message object or a Template object.
        Ignores reource from JID if it is not present.

        Args:
          message (peak.message.Message): the message to match to

        Returns:
          bool: wether the message matches or not

        """
        if self.to:
            if self.to.domain != message.to.domain:
                return False
            if self.to.localpart and message.to.localpart != self.to.localpart:
                return False
            if self.to.resource and message.to.resource != self.to.resource:
                return False

        if self.sender:
            if self.sender.domain != message.sender.domain:
                return False
            if (
                self.sender.localpart
                and message.sender.localpart != self.sender.localpart
            ):
                return False
            if self.sender.resource and message.sender.resource != self.sender.resource:
                return False

        if self.body and message.body != self.body:
            return False

        if self.thread and message.thread != self.thread:
            return False

        for key, value in self.metadata.items():
            if key not in message.metadata:
                return False
            if value is not None and message.get_metadata(key) != value:
                return False

        logger.debug(f"message matched {self} == {message}")
        return True
