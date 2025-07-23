from typing import Type

from spade.message import MessageBase as _MessageBase
from spade.template import Template as SpadeTemplate

from peak.logging import getLogger

logger = getLogger(__name__)


class Template(SpadeTemplate):
    """PEAK's template for matching messages."""

    def match(self, message: Type["_MessageBase"]) -> bool:
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
            if message.get_metadata(key) != value:
                return False

        logger.debug(f"message matched {self} == {message}")
        return True
