from typing import Union

from aioxmpp import JID

class _NotAGroupException(Exception):pass

def from_group(jid: Union[JID, str]):
    if isinstance(jid, JID):
        jid = str(jid)
    return 'conference' in jid

def name(jid: Union[JID, str]):
    '''
    Gets the user name from a JID
    '''

    if isinstance(jid, str):
        jid = JID.fromstr(jid)
    if 'conference' in jid.domain:
        return jid.resource
    else:
        return jid.localpart

def group(jid: Union[JID, str]):
    '''
    Gets the group from a JID.
    
    Throws error if it is not form a group.
    '''

    if isinstance(jid, str):
        jid = JID.fromstr(jid)
    if 'conference' in jid.domain:
        return jid.localpart
    else:
        raise _NotAGroupException()

def sender_jid(group_jid: Union[JID, str]):
    '''
    Gets sender JID from a group JID.
    '''
    if isinstance(group_jid, str):
        jid = JID.fromstr(group_jid)
    return name(group_jid) + '@' + jid.domain.replace('conference.', '')


if __name__ == '__main__':
    jid = 'test@localhost'
    gjid = 'main@conference.localhost/test'
    assert not from_group(jid)
    assert from_group(gjid)
    assert 'test' == name(jid)
    assert jid == sender_jid(gjid)
    assert 'main' == group(gjid)
