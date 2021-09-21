import logging as _logging

import aioxmpp
import aioxmpp.callbacks
import spade
import spade.agent
import spade.behaviour
import spade.message


_logger = _logging.getLogger('mas.Agent')


class Agent(spade.agent.Agent):
    '''This class integrates the XMPP Multi-User Chat (MUC) feature into the SPADE arquitecture.
    '''
    
    class DFRegister(spade.behaviour.OneShotBehaviour):

        async def run(self):
            msg = spade.message.Message()
            msg.to = 'df@' + self.agent.jid.domain
            msg.set_metadata('register', 'agent')
            msg.set_metadata('types', self.setToString(self.agent.group_names))
            await self.send(msg)

        def setToString(self, value):
            s = ''
            for v in value:
                s += v + ';'
            return s[:len(s)-1]

    def __init__(self, name, server, mas_name, group_names: set[str] = {}, verify_security=False):
        self.rooms = dict()
        self.muc_client = None
        self.mas_name = mas_name
        self.group_names = group_names
        self.room_jids = None
        self.server = server
        jid = name + '@' + server
        super().__init__(jid, jid, verify_security)
        self.add_behaviour(self.DFRegister())

    async def _hook_plugin_after_connection(self):
        '''
        Executed after SPADE Agent's connection.

        This method adds the MUC service to the Agent XMPP Client and
        adds a message dispatcher for the group(MUC) messages.
        '''
        self.muc_client = self.client.summon(
                    aioxmpp.MUCClient)
        self.message_dispatcher.register_callback(
            aioxmpp.MessageType.GROUPCHAT, None, self._message_received,
        )
        self._join_mucs()

    def _create_muc_jids(self):
        '''
        Creates JIDs based on the groups' names'''

        muc_jids = set()
        room_jids = dict()

        mas_muc_jid = self.mas_name + '@conference.' + self.jid.domain
        muc_jids.add(mas_muc_jid)
        room_jids[self.mas_name] = mas_muc_jid

        for name in self.group_names:
            jid = name + '-at-' + mas_muc_jid
            muc_jids.add(jid)
            room_jids[name] = jid

        return muc_jids, room_jids

    def _on_muc_failure_handler(self, exc):
        '''
        Handles MUC failed connections.
        '''
        
        _logger.critical('Failed to enter MUC room: ' + str(self.agent.jid))
        raise exc

    def _join_mucs(self):
        '''
        Connects Agent to the XMPP room.
        '''

        muc_jids, self.room_jids = self._create_muc_jids()
        for jid in muc_jids:
            room, _ = self.muc_client.join(
                aioxmpp.JID.fromstr(jid), self.jid.localpart)
            room.on_failure.connect(self._on_muc_failure_handler)
            self.rooms[jid] = room

    def group_members(self, group) -> list:
        '''
        Get's the list of room members in a specific room.
        '''

        jid = self.room_jids[group]
        return self.rooms[jid].members



