import aioxmpp
import aioxmpp.forms.xso as forms_xso
from aioxmpp import MessageType
from spade.message import SPADE_X_METADATA
from spade.message import Message as _SpadeMessage

from peak.logging import getLogger

logger = getLogger(__name__)


class Message(_SpadeMessage):
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
