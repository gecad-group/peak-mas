from abc import ABCMeta

import aioxmpp
import spade.behaviour

import mas


class _MUCBehaviour:

    async def send_to_group(self, msg: mas.Message, group = None, *, leave = False):
        jid = ''
        mas_muc_jid = self.agent.mas_name + '@conference.' + self.agent.jid.domain
        if group:
            jid = group + '-at-' + mas_muc_jid
        else:
            jid = mas_muc_jid
        msg = msg.prepare()
        await self._send_to_group(msg, jid, leave)

    async def _send_to_group(self, msg, muc_jid, leave = False):    
        room, future = self.agent.muc_client.join(
                aioxmpp.JID.fromstr(muc_jid), self.agent.jid.localpart)
        await future
        await room.send_message(msg)
        if leave:
            await room.leave()


class OneShotBehaviour(spade.behaviour.OneShotBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass
    #async def receive(self, timeout: float = None) -> Union[spade.message.Message, None]:
    #    return mas.message.MUCMessage.from_message(await super().receive(timeout=timeout))

class PeriodicBehaviour(spade.behaviour.PeriodicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class CyclicBehaviour(spade.behaviour.CyclicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class FSMBehaviour(spade.behaviour.FSMBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass