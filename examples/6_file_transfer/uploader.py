import os
from mimetypes import guess_type

import requests
from aioxmpp import JID
from aioxmpp.httpupload import request_slot
from aioxmpp.httpupload.xso import Slot

from peak import Agent, OneShotBehaviour


class uploader(Agent):
    class UploadFile(OneShotBehaviour):
        async def run(self):
            filename = "dataset.txt"
            filetype, enconding = guess_type(filename)
            filesize = os.stat(filename).st_size
            slot: Slot = await request_slot(
                self.agent.client,
                JID.fromstr("localhost"),
                filename,
                filesize + 10000,
                filetype,
            )
            print(slot.put.url)
            print(slot.get.url)
            with open(filename) as file:
                r = requests.put(
                    slot.put.url,
                    headers=slot.put.headers,
                    files={filename: file},
                    verify=False,
                )
            print(r)

    async def setup(self):
        self.add_behaviour(self.UploadFile())
