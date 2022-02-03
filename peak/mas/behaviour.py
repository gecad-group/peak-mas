from abc import ABCMeta

import spade.behaviour

from peak.mas import Message


class _MUCBehaviour:

    async def send_to_group(self, msg: Message):
        """Sends a message to a group chat.

        When sending a message to a group the agent joins the group first. The parameter
        'leave' tells the method if the agent leaves, or not, the group after sending the 
        message. (If the intention is to send a single request to a new group the best 
        option would be to leave the group chat, if the intention is to send a message 
        to a group wich the agent already belongs to, it's better to not leave)
        Args:
            msg (mas.Message): The Message.
            group (str, optional): Name of the group to send the message to. If None is given the
                                   the message is sent to the MAS group. Defaults to None.
            leave (bool, optional): If true, agent leaves the group after sending the message. Defaults to False.
        """   
        raw_msg = msg.prepare()
        try:
            await self.agent.groups[str(msg.to)].send_message(raw_msg)
        except:
            room, future = self.agent.muc_client.join(msg.to, self.agent.name)
            await future
            await room.send_message(raw_msg)
            await room.leave()


class OneShotBehaviour(spade.behaviour.OneShotBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class PeriodicBehaviour(spade.behaviour.PeriodicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class CyclicBehaviour(spade.behaviour.CyclicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class FSMBehaviour(spade.behaviour.FSMBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass