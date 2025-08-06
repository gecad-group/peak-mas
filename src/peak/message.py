from typing import Union

import aioxmpp
import aioxmpp.forms.xso as forms_xso
from aioxmpp import JID, MessageType
from spade.message import SPADE_X_METADATA
from spade.message import Message as _Message
from spade.message import MessageBase as _MessageBase

from peak.logging import getLogger

logger = getLogger(__name__)


class MessageBase(_MessageBase):
    @property
    def to(self) -> aioxmpp.JID:
        """
        Gets the jid of the receiver.

        Returns:
          aioxmpp.JID: jid of the receiver

        """
        return self._to

    @to.setter
    def to(self, jid: Union[str, JID]) -> None:
        """
        Set jid of the receiver.

        Args:
          jid (str): the jid of the receiver.

        """
        if isinstance(jid, JID):
            self._to = jid
            return
        if isinstance(jid, str):
            self._to = JID.fromstr(jid)
        if jid is not None and not isinstance(jid, str) and not isinstance(jid, JID):
            raise TypeError("'to' MUST be a string or a JID")

    @property
    def sender(self) -> aioxmpp.JID:
        """
        Get jid of the sender

        Returns:
          aioxmpp.JID: jid of the sender

        """
        return self._sender

    @sender.setter
    def sender(self, jid: Union[str, JID]) -> None:
        """
        Set jid of the sender

        Args:
          jid (str): jid of the sender

        """
        if isinstance(jid, JID):
            self._sender = jid
            return
        if isinstance(jid, str):
            self._sender = JID.fromstr(jid)
        if jid is not None and not isinstance(jid, str) and not isinstance(jid, JID):
            raise TypeError("'sender' MUST be a string or a JID")


class Message(MessageBase, _Message):
    def prepare(self) -> aioxmpp.Message:
        """
        Returns an aioxmpp.stanza.Message built from the Message and prepared to be sent.

        Returns:
          aioxmpp.stanza.Message: the message prepared to be sent

        """
        msg = aioxmpp.stanza.Message(
            to=self.to,
            from_=self.sender,
            type_=MessageType.CHAT,
        )

        msg.body[None] = self.body

        # Send metadata using xep-0004: Data Forms (https://xmpp.org/extensions/xep-0004.html)
        if len(self.metadata) or self.thread:
            data = forms_xso.Data(type_=forms_xso.DataType.FORM)

            for name, value in self.metadata.items():
                data.fields.append(
                    forms_xso.Field(
                        var=name,
                        type_=forms_xso.FieldType.TEXT_SINGLE,
                        values=[value],
                    )
                )

            if self.thread:
                data.fields.append(
                    forms_xso.Field(
                        var="_thread_node",
                        type_=forms_xso.FieldType.TEXT_SINGLE,
                        values=[self.thread],
                    )
                )

            data.title = SPADE_X_METADATA
            msg.xep0004_data = [data]

        return msg
