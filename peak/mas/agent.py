import logging as _logging
from typing import List, Union

import aioxmpp as _aioxmpp
from aioxmpp import JID
import spade as _spade


_logger = _logging.getLogger(__name__)


class _XMPPAgent(_spade.agent.Agent):
    '''This class integrates the XMPP Multi-User Chat (MUC) feature into the SPADE arquitecture.
    '''

    def __init__(self, jid: JID, verify_security=False):
        """Agent base class.

        Args:
            name (str): Name of the agent.
            server (str): Domain of the XMPP server to connect the agent to.
            verify_security (bool, optional): Wether to verify or not the SSL certificates. Defaults to False.
        """
        self.groups = dict()
        self.muc_client = None
        pw = str(jid.bare())
        jid = str(jid)
        super().__init__(jid, pw, verify_security)

    async def _hook_plugin_after_connection(self):
        '''
        Executed after SPADE Agent's connection.

        This method adds the MUC service to the Agent XMPP Client and
        adds a message dispatcher for the group(MUC) messages.
        '''
        self.presence.approve_all = True
        self.muc_client = self.client.summon(
                    _aioxmpp.MUCClient)
        self.message_dispatcher.register_callback(
            _aioxmpp.MessageType.GROUPCHAT, None, self._message_received,
        )

        self.pubsub_client = self.client.summon(
                    _aioxmpp.PubSubClient)

    def _on_muc_failure_handler(self, exc):
        '''
        Handles MUC failed connections.
        '''
        
        _logger.critical('Failed to enter MUC room')
        raise exc

    async def join_group(self, jid):
        _logger.info('joining group: ' + jid)
        room, fut = self.muc_client.join(_aioxmpp.JID.fromstr(jid), self.name)
        room.on_failure.connect(self._on_muc_failure_handler)
        await fut
        self.groups[jid] = room

    async def leave_group(self, jid):
        _logger.info('leaving group: ' + jid)
        room = self.groups.pop(jid, None)
        await room.leave()
            
    def group_members(self, jid) -> List:
        """Extracts list of group members from a group chat.

        Args:
            group (str): Name of the group. Must be registered previously in the gorup

        Returns:
            List: A copy of the list of occupants. The local user is always the first item in the list. 
        """

        return self.groups[jid].members



    



class Agent(_XMPPAgent):

    def __init__(self, jid: JID, properties=None, verify_security=False):
        super().__init__(jid, verify_security=verify_security)
        if properties:
            self.properties = properties
            self._parse(properties)

    def iterate_properties(self):
        for key in self.properties:
            getattr(self, key).next()

    def _parse(self, properties):
        for key in properties:
            setattr(self, key, properties[key])
