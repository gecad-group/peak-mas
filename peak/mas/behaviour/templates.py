from abc import ABCMeta, abstractmethod

import spade.behaviour
from spade.message import Message

from peak.mas import Agent

from aioxmpp import JID
import aioxmpp 

def slice_jid(jid):
    jid = JID.fromstr(jid)
    pubsub = JID.fromstr(jid.domain)
    node = jid.localpart
    return pubsub, node

class _MUCBehaviour:

    agent:Agent

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

    async def change_node_affiliations(self, jid: str, affiliations_to_set: tuple):
        """Changes PubSub node affiliations.

        Args:
            jid (str): JID of the node, e.g. node@pubsub.example.com
            affiliations_to_set (tuple[str,str]): each tuple must contain the JID of the user and the affiliation (e.g.'owner','publisher')
        """
        pubsub, node = slice_jid(jid)
        user, aff = affiliations_to_set
        await self.agent.pubsub_client.change_node_affiliations(pubsub, node, [(JID.fromstr(user), aff)])

    async def subscribe(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.subscribe(pubsub, node)

    async def publish(self, msg: Message):
        jid = msg.to.domain
        node = msg.to.localpart
        aioxmpp.pubsub.xso.as_payload_class(aioxmpp.Message)
        await self.agent.pubsub_client.publish(JID.fromstr(jid), node, msg.prepare())

    async def notify(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.notify(pubsub, node)

    async def unsubscribe(self, jid: str):
        pubsub, node = slice_jid(jid)
        await self.agent.pubsub_client.unsubscribe(pubsub, node)

    @abstractmethod
    def on_item_published(jid, node, item, *, message=None):
        pass

class OneShotBehaviour(spade.behaviour.OneShotBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class PeriodicBehaviour(spade.behaviour.PeriodicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class CyclicBehaviour(spade.behaviour.CyclicBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass

class FSMBehaviour(spade.behaviour.FSMBehaviour, _MUCBehaviour, metaclass=ABCMeta):pass