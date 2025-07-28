from time import sleep

from peak import JID, DummyAgent, Message


def send_message(
    to: JID, sender: JID, body: str, thread: str, metadata: dict, *args, **kargs
):
    if sender is None:
        sender = f"dummyagent@{to.domain}/main"
    msg = Message(
        to=str(to), sender=str(sender), body=body, thread=thread, metadata=metadata
    )
    print(to, sender, body, msg.sender, type(msg.sender))
    da = DummyAgent(jid=msg.sender, message=msg)
    da.start().result()
    while da.is_alive():
        sleep(0.5)
