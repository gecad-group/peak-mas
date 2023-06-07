from peak import Agent, OneShotBehaviour
from aioxmpp.httpupload import request_slot
from aioxmpp.httpupload.xso import Slot
from aioxmpp import JID
from mimetypes import guess_type
import os
import requests

class uploader(Agent):
    class UploadFile(OneShotBehaviour):
        async def run(self):
            filename = "dataset.txt"
            filetype, enconding = guess_type(filename)
            filesize = os.stat(filename).st_size
            print(filetype)
            print(filesize)
            slot: Slot = await request_slot(self.agent.client, JID.fromstr("upload.localhost"), filename, filesize, filetype)
            print(slot)
            with open(filename) as file:
                r = requests.put(slot.put.url, headers=slot.put.headers, data=file)
            print(r.json())

    async def setup(self):
        self.add_behaviour(self.UploadFile())