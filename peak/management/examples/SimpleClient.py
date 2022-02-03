import aioxmpp
import aioxmpp.ibr as ibr
import asyncio

DF_JID = "df@localhost"


async def main():
    recipient_jid = aioxmpp.JID.fromstr("coco@localhost")
    jid = aioxmpp.JID.fromstr(DF_JID)
    password = DF_JID

    metadata = aioxmpp.make_security_layer(None, no_verify=True)
    query = ibr.Query(jid.localpart, password)
    _, stream, features = await aioxmpp.node.connect_xmlstream(jid, metadata)
    await ibr.register(stream, query)

    client = aioxmpp.cli.PresenceManagedClient(
            jid,
            aioxmpp.make_security_layer(password, no_verify=True)
        )

    async with client.connected() as stream:
        msg = aioxmpp.Message(
            to=recipient_jid,  # recipient_jid must be an aioxmpp.JID
            type_=aioxmpp.MessageType.CHAT)
        # None is for "default language"
        msg.body[None] = "Hello World!"

        await client.send(msg)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())