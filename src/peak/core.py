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
        logger (:obj:`Logger`)
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
    """Adds XMPP functinalities to SPADE's base behaviours."""

    agent: Agent

    def __init__(self) -> None:
        self.logger = _logging.getLogger(self.__class__.__name__)

    async def join_group(self, jid: str):
        """Joins the agent in a group.

        Args:
            jid: Group's XMPP identifier.

        Raises:
            Exception if the group JID is invalid.
        """
        room, fut = self.muc_client.join(_aioxmpp.JID.fromstr(jid), self.name)
        room.on_failure.connect(self._on_muc_failure_handler)
        try:
            await first_signal(room.on_enter, room.on_failure)
        except Exception as e:
            self.logger
        await _asyncio.wait([fut], timeout=3)
        if fut.done():
            if jid not in self.groups:
                self.groups[jid] = room
                self.logger.debug("joined group: " + jid)
        else:
            raise Exception("invalid group JID: " + str(jid))

    async def leave_group(self, jid: str):
        """Leaves a group.

        Args:
            jid (str): Group's XMPP identifier.
        """
        room = self.groups.pop(jid, None)
        if room:
            _logger.info("leaving group: " + jid)
            await room.leave()

    async def list_groups(self, node_jid: str):
        """Retrieves the list of the existing groups in the server.

        Args:
            node_jid: JID of the domain responsable for the MUC functionality.

        Returns:
            A list of XMPP groups.
        """
        info = await self.disco.query_items(
            _aioxmpp.JID.fromstr(node_jid), require_fresh=True
        )
        return info.items

    async def group_members(self, jid: str) -> List:
        """Retrieves list of members from a group.

        Args:
            jid: Group's XMPP identifier.

        Returns:
            A copy of the list of occupants. The local user is always the first item in 
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

        If the agent is not in the group, the agent enters the room first,
        sends the message and then leaves the group.

        Args:
            msg: The XMPP message.
        """
        raw_msg = msg.prepare()
        _logger.debug(f"sending message '{msg.body}' to {msg.to}")
        try:
            await self.agent.groups[str(msg.to)].send_message(raw_msg)
        except:
            _logger.debug(f"agent not member of {msg.to}, sending message anyway")
            room, future = self.agent._muc_client.join(msg.to, self.agent.name)
            await future
            await room.send_message(raw_msg)
            await room.leave()
            _logger.debug(f"leaving {msg.to}")

    async def wait_for(
        self,
        behaviour: _spade.behaviour.CyclicBehaviour,
        template: _spade.template.Template = None,
    ):
        """Awaits synchronozly for a behaviour.

        Executes behaviour first, if not executed.
        It is used to chain behviour that are dependent on each other.

        Args:
            behaviour: SPADE's behaviour.
        """
        if not behaviour.is_running:
            self.agent.add_behaviour(behaviour, template)
        await behaviour.join()


class OneShotBehaviour(
    _spade.behaviour.OneShotBehaviour, _Behaviour, metaclass=_ABCMeta
):
    """This behaviour is only executed once."""
    def __init__(self):
        super().__init__()


class PeriodicBehaviour(
    _spade.behaviour.PeriodicBehaviour, _Behaviour, metaclass=_ABCMeta
):
    """This behaviour is executed periodically with an interval."""


class CyclicBehaviour(_spade.behaviour.CyclicBehaviour, _Behaviour, metaclass=_ABCMeta):
    """This behaviour is executed cyclically until it is stopped."""


class FSMBehaviour(_spade.behaviour.FSMBehaviour, _Behaviour, metaclass=_ABCMeta):
    """A behaviour composed of states (oneshotbehaviours) that may transition from one 
    state to another."""
