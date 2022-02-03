import aioxmpp
import asyncio

DF_JID = "df@localhost"

jid = aioxmpp.JID.fromstr(DF_JID)
password = DF_JID
 
client = aioxmpp.PresenceManagedClient( 
    jid,
    aioxmpp.make_security_layer(password, no_verify=True)
)

async def test():
    try:
        print("pila")
        async with client.connected() as stream:
            print(await adhoc.supports_commands(aioxmpp.JID.fromstr("localhost")))
        print("cona")
    except Exception:
        print("coinhas")

adhoc = aioxmpp.AdHocClient(client)

loop = asyncio.get_event_loop()
loop.run_until_complete(test())