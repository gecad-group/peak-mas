import asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from typing import Dict, List, Optional

import aioxmpp as _aioxmpp
import spade as _spade
from aioxmpp import JID
from aioxmpp.callbacks import first_signal

_module_logger = _logging.getLogger(__name__)


class Agent(_spade.agent.Agent):
    """PEAK's base agent.

    Attributes:
        communities (dict of :obj:`Room`): Dictionary of the communities joined.
        cid (int): Clone ID.
    """

    def __init__(self, jid: JID, cid: int = 0, verify_security: bool = False):
        """Inits an agent with a JID.

        Args:
            jid (:obj:`JID`): The agent XMPP identifier.
            verify_security (bool, optional): If True, verifies the SSL certificates.
                Defaults to False.
        """
        super().__init__(str(jid), str(jid.bare()), verify_security=verify_security)
        self.communities: Dict[str, _aioxmpp.muc.Room] = dict()
        self.cid = cid
        self._muc_client = None

    async def _hook_plugin_after_connection(self):
        """Executed after SPADE Agent's connection.

        This method adds the MUC service to the Agent XMPP Client and
        adds a message dispatcher for the group(MUC) messages.
        """
        self.presence.approve_all = True
        self._muc_client: _aioxmpp.MUCClient = self.client.summon(_aioxmpp.MUCClient)
        self._disco: _aioxmpp.DiscoClient = self.client.summon(_aioxmpp.DiscoClient)
        self.message_dispatcher.register_callback(
            _aioxmpp.MessageType.GROUPCHAT,
            None,
            self._message_received,
        )
        self.message_dispatcher.register_callback(
            _aioxmpp.MessageType.NORMAL,
            None,
            self._message_received,
        )


class _BehaviourMixin:
    """Adds XMPP functinalities to SPADE's base behaviours.

    Acts as Mixin in the SPADE's behaviours.

    Attributes:
        logger (:obj:`Logger`): Used to log every event in a behaviour."""

    agent: Agent
    _logger = _module_logger.getChild("_Behaviour")

    async def receive(
        self, timeout: Optional[float] = None
    ) -> Optional[_spade.message.Message]:
        """
        Receives a message for this behaviour and waits `timeout` seconds.
        If timeout is `None`, it will wait until it receives a message.

        Note: Redefinition of the receive method of SPADE Behaviours

        Args:
            timeout (float, optional): number of seconds until return

        Returns:
            Message | None
        """
        coro = self.queue.get()
        try:
            msg = await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            msg = None
        return msg

    async def join_community(self, jid: str):
        """Joins a community.

        Args:
            jid (str): XMPP identifier of the community.

        Raises:
            Exception if the community JID is invalid.
        """
        if jid not in self.agent.communities:
            room, _ = self.agent._muc_client.join(
                _aioxmpp.JID.fromstr(jid), self.agent.name
            )
            try:
                await first_signal(room.on_enter, room.on_failure)
                self.agent.communities[jid] = room
                self._logger.debug(f"Joined community: {jid}")
            except Exception as error:
                self._logger.exception(
                    f"Couldn't join community (reason: {error}):  {jid}"
                )
        else:
            self._logger.debug(f"Already joined this community: {jid}")

    async def leave_community(self, jid: str):
        """Leaves a community.

        Args:
            jid (str): XMPP identifier of the community.
        """
        room = self.agent.communities.pop(jid, None)
        if room:
            await room.leave()
            self._logger.debug(f"Left community: {jid}")

    async def list_communities(self, node_jid: str):
        """Retrieves the list of the existing community in the server.

        This method uses the Service Discovery functionality of the XMPP
        server. In orther to work the server must have this functionality
        configured.

        Args:
            jid: XMPP identifier of the Service Discovery domain.

        Returns:
            A list of XMPP communities.
        """
        info = await self.agent._disco.query_items(
            _aioxmpp.JID.fromstr(node_jid), require_fresh=True
        )
        return info.items

    async def community_members(self, jid: str) -> List[_aioxmpp.muc.Occupant]:
        """Retrieves list of members from a community.

        If the agent is not a member of the community, it will enter the room ,
        retrieve the list of members and then leave the community.

        Args:
            jid: XMPP identifier of the community.

        Returns:
            The list of :obj:`Occupants`. The agent is always the first item in
            the list, unless it's not a member.
        """
        if jid in self.agent.communities:
            return self.agent.communities[jid].members
        else:
            await self.join_community(jid)
            members = self.agent.communities[jid].members
            await self.leave_community(jid)
            return members[1:]

    async def send_to_community(self, msg: _spade.message.Message):
        """Sends a message to a community.

        If the agent is not a member of the community, the agent enters the room first,
        sends the message and then leaves the community.

        Args:
            msg: The XMPP message.
        """
        raw_msg = msg.prepare()
        self._logger.debug(f"Sending message: {msg}")
        group = str(msg.to)
        try:
            await self.agent.communities[group].send_message(raw_msg)
        except:
            self._logger.debug(
                f"Sending a message to a group which the agent is not a member of: {group}"
            )
            await self.join_community(group)
            await self.agent.communities[group].send_message(raw_msg)
            await self.leave_community(group)

    async def wait_for(
        self,
        behaviour: _spade.behaviour.CyclicBehaviour,
        template: _spade.template.Template = None,
    ):
        """Awaits synchronously for a behaviour.

        Executes behaviour first, if not executed.
        It is used to chain behviours that are dependent on each other.

        Args:
            behaviour: SPADE's behaviour.
            tempalte: SPADE's template.
        """
        self._logger.debug(f"Waiting for behaviour: {behaviour}")
        if not behaviour.is_running:
            self.agent.add_behaviour(behaviour, template)
        await behaviour.join()


class OneShotBehaviour(
    _BehaviourMixin, _spade.behaviour.OneShotBehaviour, metaclass=_ABCMeta
):
    """This behaviour is only executed once."""


class PeriodicBehaviour(
    _BehaviourMixin, _spade.behaviour.PeriodicBehaviour, metaclass=_ABCMeta
):
    """This behaviour is executed periodically with an interval."""


class CyclicBehaviour(
    _BehaviourMixin, _spade.behaviour.CyclicBehaviour, metaclass=_ABCMeta
):
    """This behaviour is executed cyclically until it is stopped."""


class FSMBehaviour(_BehaviourMixin, _spade.behaviour.FSMBehaviour, metaclass=_ABCMeta):
    """A behaviour composed of states (oneshotbehaviours) that may transition from one
    state to another."""
