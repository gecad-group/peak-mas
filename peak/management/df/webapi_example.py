import sys, threading
from json import JSONDecodeError

import mas
import asyncio
import json
from aiohttp import web
import aiohttp_cors

sys.path.append('C:/Users/hjvp1/Documents/Helder/GECAD/Tese/masframework')
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

needsBody = ["/mobilityRequest"]
neededHeaders = {
    "/mobilityOptions": ["player"]
}


async def verifyRequest(request, requestNeedsBody, requestNeededHeaders):
    body = None

    try:
        requestId = request.headers["id"]
    except KeyError:
        return -1, "Missing ID", True

    try:
        if requestNeedsBody:
            body = await request.json()

        for header in requestNeededHeaders:
            request.headers[header]

    except JSONDecodeError:
        return -1, "JSON Decode Error", True
    except KeyError:
        return -1, "Missing header: " + header, True

    return requestId, body, False


class GatewayAgent(mas.Agent):

    def __init__(self, name: str, server: str, mas_name={}):
        self.httpResponse = {}
        self.messagesToSend = []
        self.requestsInProcess = []
        super().__init__(name=name, server=server, mas_name=mas_name)

    async def setup(self):
        self.add_behaviour(self.ProcessMessages())
        self.web.add_get("/{path}", self.getRequest, template=None)

        # Configure default CORS settings.
        cors = aiohttp_cors.setup(self.web.app, defaults={
            "*": aiohttp_cors.ResourceOptions(
                allow_credentials=True,
                expose_headers="*",
                allow_headers="*",
            )
        })

        # Configure CORS on all routes.
        for route in list(self.web.app.router.routes()):
            cors.add(route)

        self.web.start(port=10000)

    async def getRequest(self, request):
        if request.path != '/favicon.ico':
            requestId, body, error = await verifyRequest(request, request.path in needsBody,
                                                         neededHeaders[request.path])

            if requestId != -1:
                if requestId not in self.requestsInProcess:
                    self.requestsInProcess.append(requestId)
                    self.httpResponse[requestId] = None

                    if request.path == "/mobilityOptions":
                        self.mobilityOptions(requestId, request.headers)
                    elif request.path == "/mobilityRequest":
                        self.mobilityRequest(requestId, body)

                elif self.httpResponse[requestId] is not None:
                    self.requestsInProcess.remove(requestId)
                    return self.httpResponse[requestId]
            else:
                if error:
                    return {"error": body}
                else:
                    print("NO ID")
                    return {"error": "No ID"}

        '''msg = await self.receive(timeout=0.5)
        if msg:
            requestIdMessage = msg.get_metadata("requestId")
            if requestIdMessage == requestId:
                return json.loads(msg.body)
            else:
                self.agent.httpResponse[requestIdMessage] = json.loads(msg.body)'''

        '''messageBehaviour = self.WaitForMessageAndReturn()
        messageBehaviour.set_agent(self)
        await messageBehaviour.run()

        if messageBehaviour.get("requestId") == requestId:
            return messageBehaviour.get("response")
        else:
            self.httpResponse[messageBehaviour.get("requestId")] = messageBehaviour.get("response")'''

        return {}

    def mobilityOptions(self, requestId, headers):
        player = headers["player"]
        message = mas.Message()
        message.sender = self.jid_string
        message.to = player + "@" + self.jid.domain
        message.set_metadata("requestId", requestId)
        message.set_metadata("requestType", "mobilityOptions")
        self.messagesToSend.append(message)

    def mobilityRequest(self, requestId, body):
        player = body["player"]
        chosenMas = body["chosenMas"]

        message = mas.Message()
        message.sender = self.jid_string
        message.to = player + "@" + self.jid.domain
        message.body = json.dumps({"chosenMas": chosenMas})
        message.set_metadata("requestId", requestId)
        message.set_metadata("requestType", "mobilityRequest")
        self.messagesToSend.append(message)

    class ProcessMessages(mas.CyclicBehaviour):

        async def run(self):
            msg = await self.receive()
            if msg:
                requestId = msg.get_metadata("requestId")
                self.agent.httpResponse[requestId] = json.loads(msg.body)

            if len(self.agent.messagesToSend) != 0:
                for message in self.agent.messagesToSend:
                    await self.send(message)
                self.agent.messagesToSend = []

    class WaitForMessageAndReturn(mas.OneShotBehaviour):

        async def run(self):
            msg = await self.receive(timeout=1)
            if msg:
                requestIdMessage = msg.get_metadata("requestId")
                self.set("requestId", requestIdMessage)
                self.set("response", json.loads(msg.body))
