from peak import Agent, OneShotBehaviour
import requests

class downloader(Agent):
    class DownloadFile(OneShotBehaviour):
        async def run(self):
            url = "https://localhost:5281/file_share/2SrmubaGcRGhoXXh/dataset.txt"
            r = requests.get(url, verify=False)
            print(r)

    async def setup(self):
        self.add_behaviour(self.DownloadFile())