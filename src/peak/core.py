# Standard library imports
import asyncio as _asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from typing import Any, List
from aioxmpp.callbacks import first_signal

# Third party imports
import aioxmpp as _aioxmpp
import spade as _spade
from aioxmpp import JID



class Agent(_spade.agent.Agent):
    """PEAK's base agent.

    Attributes:
        groups (list of :obj:`Room`): Has all the groups that the agent is member of.
        logger (:obj:`Logger`): Used to log all the necessary events in the agent.
    """

    def __init__(self, jid: JID, verify_security: bool = False):
        """Inits an agent with a JID.

        Args:
            jid (:obj:`JID`): The agent XMPP identifier.
            verify_security (bool, optional): If True, verifies the SSL certificates. 
                Defaults to False.
        """
        super().__init__(str(jid), str(jid.bare()), verify_security)
        self.groups = dict()
        self._muc_client = None
        self.logger = _logging.getLogger(jid.localpart)
        self.logger.setLevel(_logging.DEBUG) #TODO: test if it works with the cli log_level configuration
    
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


class _Behaviour:
    """Adds XMPP functinalities to SPADE's base behaviours.
    
    Acts as Mixin in the SPADE's behaviours.
    
    Attributes:
        logger (:obj:`Logger`): Used to log every event in a behaviour."""

    agent: Agent

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.logger = self.agent.logger.getChild(self.__class__.__name__)

    async def join_group(self, jid: str):
        """Joins a group.

        Args:
            jid (str): Group's XMPP identifier.

        Raises:
            Exception if the group JID is invalid.
        """
        room, _ = self.muc_client.join(_aioxmpp.JID.fromstr(jid), self.name)
        try:
            await first_signal(room.on_enter, room.on_failure)
            self.groups[jid] = room
            self.logger.info(f"Joined group: {jid}")
        except Exception as error:
            self.logger.exception(f"Couldn't join group (reason: {error}):  {jid}")

    async def leave_group(self, jid: str):
        """Leaves a group.

        Args:
            jid (str): Group's XMPP identifier.
        """
        room = self.groups.pop(jid, None)
        if room:
            await room.leave()
            self.logger.info("Left group: {jid}")

    async def list_groups(self, node_jid: str):
        """Retrieves the list of the existing groups in the server.

        This method uses the Service Discovery functionality of the XMPP 
        server. In orther to work the server must have this functionality 
        configured.

        Args:
            jid: XMPP identifier of the Service Discovery domain.

        Returns:
            A list of XMPP groups.
        """
        info = await self.disco.query_items(
            _aioxmpp.JID.fromstr(node_jid), require_fresh=True
        )
        return info.items

    async def group_members(self, jid: str) -> List:
        """Retrieves list of members from a group.

        If the agent is not a member of the group, it will enter the room , 
        retrieve the list of members and then leave the group.

        Args:
            jid: Group's XMPP identifier.

        Returns:
            The list of :obj:`Occupants`. The local user is always the first item in 
            the list.
        """
        if jid in self.groups:
            return self.groups[jid].members
        else:
            await self.join_group(jid)
            members = self.groups[jid].members
            await self.leave_group(jid)
            return members

    async def send_to_group(self, msg: _spade.message.Message):
        """Sends a message to a group.

        If the agent is not a member of the group, the agent enters the room first,
        sends the message and then leaves the group.

        Args:
            msg: The XMPP message.
        """
        raw_msg = msg.prepare()
        self.logger.debug(f"Sending message: {msg}")
        group = str(msg.to)
        try:
            await self.agent.groups[group].send_message(raw_msg)
        except:
            self.logger.warning(f"Sending a message to a group which the agent is not a member of: {group}")
            await self.join_group(group)
            await self.group[group].send_message(raw_msg)
            await self.leave_group(group)

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
        if not behaviour.is_running:
            self.agent.add_behaviour(behaviour, template)
        await behaviour.join()


class OneShotBehaviour(
    _Behaviour, _spade.behaviour.OneShotBehaviour, metaclass=_ABCMeta
):
    """This behaviour is only executed once."""


class PeriodicBehaviour(
    _Behaviour, _spade.behaviour.PeriodicBehaviour, metaclass=_ABCMeta
):
    """This behaviour is executed periodically with an interval."""


class CyclicBehaviour(_Behaviour, _spade.behaviour.CyclicBehaviour, metaclass=_ABCMeta):
    """This behaviour is executed cyclically until it is stopped."""


class FSMBehaviour(_Behaviour, _spade.behaviour.FSMBehaviour, metaclass=_ABCMeta):
    """A behaviour composed of states (oneshotbehaviours) that may transition from one 
    state to another."""
