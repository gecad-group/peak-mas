from typing import Union as _Union

from aioxmpp import JID as _JID


def from_group(jid: _Union[_JID, str]):
    """Checks if JID is from a group or not.

    Args:
        jid (Union[JID, str]): JID

    Returns:
        bool: True if is group JID, False if it is a user JID.
    """
    if isinstance(jid, _JID):
        jid = str(jid)
    return 'conference' in jid


def name(jid: _Union[_JID, str]):
    """Gets the user name from a JID.

    Args:
        jid (Union[JID, str]): JID

    Returns:
        str: Name of the JID's User.
    """
    if isinstance(jid, str):
        jid = _JID.fromstr(jid)
    if 'conference' in jid.domain:
        return jid.resource
    else:
        return jid.localpart


def group(jid: _Union[_JID, str]):
    """Gets the group name from a JID.

    Args:
        jid (Union[JID, str]): JID

    Returns:
        str: If it is a group JID, returns the group name.
        None: If it's not a group JID.    
    """
    if isinstance(jid, str):
        jid = _JID.fromstr(jid)
    if 'conference' in jid.domain:
        return jid.localpart


def sender_jid(group_jid: _Union[_JID, str]):
    """Gets sender JID from a group JID.

    Args:
        group_jid (Union[JID, str]): Group JID.

    Returns:
        str: JID of the sender.
    """
    if isinstance(group_jid, str):
        jid = _JID.fromstr(group_jid)
    return name(group_jid) + '@' + jid.domain.replace('conference.', '')


if __name__ == '__main__':
    jid = 'test@localhost'
    gjid = 'main@conference.localhost/test'
    assert not from_group(jid)
    assert from_group(gjid)
    assert 'test' == name(jid)
    assert jid == sender_jid(gjid)
    assert 'main' == group(gjid)
