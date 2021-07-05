#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import asyncio
import json
import logging
import time
import websockets
from random import randint
from threading import Thread, Event
from websockets import WebSocketServerProtocol
import random


class ServerWS():
    clients = set()
    
    # add client to clients list
    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f"{ws.remote_address} connects.")

    # remove client from clients list
    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        await ws.close(1000,"Normal Closure")
        self.clients.remove(ws)
        logging.info(f"{ws.remote_address} disconnects.")

    # send message to one client
    async def send_to_client(self, ws: WebSocketServerProtocol, message: str) -> None:
        await ws.send(message)

    # Send message to all clients
    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    # TODO find what do this thing
    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
        await self.register(ws)
        try:
            # Start communication
            # Flush messages to the new client
            # await asyncio.wait([ self.send_to_client(ws, json.dumps( {"type": "UPDATE_SENSOR", "content": {"id": k,"value": v}})) for k,v in store_smart4l.last_measure.items()])
            await self.distribute(ws)
        finally:
            # Remove client from clients list
            await self.unregister(ws)

    # TODO find what do this thing
    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        # TODO find what do this thing
        async for message in ws:
            # await self.send_to_clients(message)
            pass

    # Close connection for all client in clients list 
    async def close_all_connections(self):
        await asyncio.wait([self.unregister(client) for client in self.clients])


from enum import Enum
import abc


class Status(Enum):
    CREATED = 'created'
    RUNNING = 'running'
    WAITING = 'waiting'
    BLOCKED = 'blocked'
    TERMINATED = 'terminated'

class RunnableObjectInterface(abc.ABC):
    @abc.abstractmethod
    def do(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass


class Smart4lWebSocket:
    def __init__(self, loop: asyncio.AbstractEventLoop, host:str, port:int):
        self.loop = loop
        self.ws_server = ServerWS()
        self.conf = {"host": host, "port": port}

    def do(self,):
        asyncio.set_event_loop(self.loop)
        start_server = websockets.serve(self.ws_server.ws_handler, self.conf["host"], self.conf["port"])
        self.loop.run_until_complete(start_server)
        self.loop.run_forever()
    
    def stop(self):
        asyncio.run_coroutine_threadsafe(self.ws_server.close_all_connections(), self.loop)
        self.loop.stop()

    def send_message(self, message:str):
        asyncio.run_coroutine_threadsafe(self.ws_server.send_to_clients(json.dumps(message)), self.loop)

class Service(Thread):
    def __init__(self, runnable_object : RunnableObjectInterface, delay : int=0):
        Thread.__init__(self)
        self.delay_between_tasks = delay
        self.runnable_object = runnable_object

        self.status = Status.CREATED.value
        self.event_stop_service = Event()

    def run(self):
        self.status = Status.RUNNING.value
        while self.status == Status.RUNNING.value:
            self.runnable_object.do()
            self.event_stop_service.wait(self.delay_between_tasks)

    def stop(self):
        self.status = Status.TERMINATED.value
        self.event_stop_service.set()
        self.runnable_object.stop()

    def __str__(self):
        return f"Current status: {self.status} - RunnableObject {str(self.runnable_object)} - Delay {str(self.delay_between_tasks)}"

    def __repr__(self):
        return str(self)


loop = asyncio.get_event_loop()
ws = Smart4lWebSocket(loop, host="0.0.0.0", port=int(os.environ["PORT"]))
Service(ws).start()


while True:
  messages = [
    {'label':'Température extérieure','serial_id':'28-01193a2abb07', 'measure': random.randint(150,350)/10, 'symbol': '°C' }
    ,{'label':'Humidité','serial_id':'', 'measure': random.randint(1,10)/10, 'symbol': '%' }
    ,{'label':'Vitesse','serial_id':'', 'measure': random.randint(0,130), 'symbol': 'Km/h' }
    ,{'label':'Inclinaison X','serial_id':'', 'measure': random.randint(0,180), 'symbol': '°' }
    ,{'label':'Inclinaison Y','serial_id':'', 'measure': random.randint(0,180), 'symbol': '°' }
    ,{'label':'Inclinaison Z','serial_id':'', 'measure': random.randint(0,180), 'symbol': '°' }
    ,{'label':'GPS latitude','serial_id':'', 'measure': random.randint(5,15)/10, 'symbol': '°' }
    ,{'label':'GPS longitude','serial_id':'', 'measure': random.randint(5,15)/10, 'symbol': '°' }
  ]
  ws.send_message(random.choice(messages))
  time.sleep(random.randint(1,20)/5)


ws.stop_websocket_server()





