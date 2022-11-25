# Standard library imports
import asyncio as _asyncio
import logging as _logging
from abc import ABCMeta as _ABCMeta
from typing import Any, List

# Third party imports
import aioxmpp as _aioxmpp
import spade as _spade
from aioxmpp import JID

_logger = _logging.getLogger(__name__)


class _XMPPAgent(_spade.agent.Agent):
    """Agent that integrates XMPP functionalities.

    Attributes:
        jid: XMPP identifier.
        verify_security: If true verifies the SSL certificates.
    """

    def __init__(self, jid: JID, verify_security: bool = False):
        _logging.getLogger(jid.localpart).setLevel(_logging.ERROR)
        self.groups = dict()
        self.muc_client = None
        pw = str(jid.bare())
        jid = str(jid)
        super().__init__(jid, pw, verify_security)

    async def _hook_plugin_after_connection(self):
        """Executed after SPADE Agent's connection.

        This method adds the MUC service to the Agent XMPP Client and
        adds a message dispatcher for the group(MUC) messages.
        """
        self.presence.approve_all = True

        self.muc_client: _aioxmpp.MUCClient = self.client.summon(_aioxmpp.MUCClient)
        self.disco: _aioxmpp.DiscoClient = self.client.summon(_aioxmpp.DiscoClient)

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

    def _on_muc_failure_handler(self, exc):
        """Handles MUC failed connections."""

        _logger.critical("Failed to enter MUC room")
        raise exc

    async def join_group(self, jid: str):
        """Joins the agent in a group.

        Args:
            jid: Group's XMPP identifier.

        Raises:
            Exception if the group JID is invalid.
        """
        room, fut = self.muc_client.join(_aioxmpp.JID.fromstr(jid), self.name)
        room.on_failure.connect(self._on_muc_failure_handler)
        await _asyncio.wait([fut], timeout=3)
        if fut.done():
            if jid not in self.groups:
                self.groups[jid] = room
                _logger.info("joined group: " + jid)
        else:
            raise Exception("invalid group JID: " + str(jid))

    async def leave_group(self, jid: str):
        """Leaves a group.

        Args:
            jid: Group's XMPP identifier.
        """
        room = self.groups.pop(jid, None)
        if room:
            _logger.info("leaving group: " + jid)
            await room.leave()

    async def list_groups(self, node_jid: str):
        """Retrieves the list of the existing groups.

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
        """Extracts list of group members from a group.

        Args:
            jid: Group's XMPP identifier.

        Returns:
            A copy of the list of occupants. The local user is always the first item in the list.
        """
        if jid in self.groups:
            return self.groups[jid].members
        else:
            await self.join_group(jid)
            members = self.groups[jid].members
            await self.leave_group(jid)
            return members


class Agent(_XMPPAgent):
    """PEAK's base agent.

    Attributes:
        jid: XMPP identifier.
        properties: Properties to be injected in the agent.
        verify_security: If True, it verifies the SSL certificates.
    """

    def __init__(self, jid: JID, properties: Any = None, verify_security: bool = False):
        """Inits Agent and fills it with properties."""
        super().__init__(jid, verify_security=verify_security)
        if properties:
            self.properties = properties
            for key in properties:
                setattr(self, key, properties[key])

    def iterate_properties(self):
        """Iterates one index over the properties."""
        if hasattr(self, "properties"):
            for key in self.properties:
                attr = getattr(self, key)
                if attr:
                    getattr(self, key).next()


class _Behaviour:
    """Adds functinality to the SPADE base behaviours."""

    agent: Agent

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
            room, future = self.agent.muc_client.join(msg.to, self.agent.name)
            await future
            await room.send_message(raw_msg)
            await room.leave()
            _logger.debug(f"leaving {msg.to}")

    async def wait_for(self, behaviour: _spade.behaviour.CyclicBehaviour):
        """Awaits synchronozly for a behaviour.

        Executes behaviour first, if not executed.
        It is used to chain behviour that are dependent on each other.

        Args:
            behaviour: SPADE's behaviour.
        """
        if not behaviour.is_running:
            self.agent.add_behaviour(behaviour)
        await behaviour.join()


class OneShotBehaviour(
    _spade.behaviour.OneShotBehaviour, _Behaviour, metaclass=_ABCMeta
):
    pass


class PeriodicBehaviour(
    _spade.behaviour.PeriodicBehaviour, _Behaviour, metaclass=_ABCMeta
):
    pass


class CyclicBehaviour(_spade.behaviour.CyclicBehaviour, _Behaviour, metaclass=_ABCMeta):
    pass


class FSMBehaviour(_spade.behaviour.FSMBehaviour, _Behaviour, metaclass=_ABCMeta):
    pass
