from peak import Agent, OneShotBehaviour
from aioxmpp.httpupload import request_slot
from aioxmpp.httpupload.xso import Slot
from aioxmpp import JID
from mimetypes import guess_type
import os
import aiohttp

class downloader(Agent):
    class UploadFile(OneShotBehaviour):
        async def run(self):
            filename = "dataset.txt"
            filetype = guess_type(filename)
            filesize = os.stat(filename).st_size
            slot: Slot = await request_slot(self.agent.client, JID.fromstr("upload@localhost"), filename, filesize, filetype)
            