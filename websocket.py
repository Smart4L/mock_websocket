#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Websocket Server Example
# https://websockets.readthedocs.io/en/stable/index.html

# - Run it -
# pip3 install websockets
# ./websocket.py

# - Deploy on Heroku -
# curl https://cli-assets.heroku.com/install.sh | sh
# heroku login
# heroku create smart4l-websockets-mock
# heroku buildpacks:set heroku/python
# git push heroku main

import asyncio
import websockets
import time
import threading
import random
import json
import os

class WebSocketServer:
  def __init__(self):
    self.running = True
    self.queue = []

  def stop(self):
    self.running = False

  async def handler(self,websocket, path):
    try:
      await websocket.send("Hello, you are now connected !")
    except:
      print(f'Erreur while connection : {websocket}')

    while self.running:
      try:        
        if len(self.queue)>0:
          await websocket.send(json.dumps(self.queue.pop(0)))
      except websockets.ConnectionClosed:
        print(f"Terminated")
        break
    print(f"Terminated {websocket}")


class WebSocketServerController:
  def __init__(self, websocket_server, loop):
    self.websocket_server=websocket_server
    self.loop=loop

  def send_message(self, message):
    self.websocket_server.queue.append(message)

  def start_websocket_server(self):    
    asyncio.set_event_loop(self.loop)
    self.server = websockets.serve(self.websocket_server.handler, "0.0.0.0", int(os.environ["PORT"]))
    loop.run_until_complete(self.server)
    loop.run_forever()

  def stop_websocket_server(self):
    self.websocket_server.stop()

loop = asyncio.get_event_loop()
ws = WebSocketServerController(WebSocketServer(),loop)

x = threading.Thread(target=ws.start_websocket_server)
x.start()

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



