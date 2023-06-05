#!/usr/bin/python3.7

import asyncio
import websockets
import _thread
import json
import uuid
import time
import sys

HOST = "localhost"
PORT = 4444

# Origin of Broadcaster
BROADCASTER = 'webots'

# Animation is used to visualize the status of the connection to the WeBots Simulation
# Animation = Getting data from Broadcaster
# No Animation = Not getting data from Broadcaster
class Animation():
    lifespan = 20
    def __init__(self):
        self.i = 0
        self.hasStarted = False
    
    def printAnimation(self):
        self.hasStarted = True
        animation = "|/-\\"
        while self.i < self.lifespan:
            time.sleep(0.1)
            sys.stdout.write("\r" + animation[self.i % len(animation)])
            sys.stdout.flush()
            self.i += 1
        self.hasStarted = False
        self.i = 0
        sys.stdout.write("\r ")

    def start(self):
        if self.hasStarted: return
        self.i = 0
        _thread.start_new_thread(self.printAnimation, ())
    
    def stop(self):
        self.i = -100
        self.hasStarted = False
    
    def keepAlive(self):
        self.i = 0

process = Animation()

class Client():
    def __init__(self, socket):
        self.uuid = uuid.uuid1()
        self.socket = socket
    
    def getUUID(self):
        return self.uuid
    
    def getSocket(self):
        return self.socket


clients = set()

def is_json(myjson):
    try:
        json.loads(myjson)
    except:
        return False
    return True

async def on_message(websocket, path):
    client = Client(websocket)
    clients.add(client)
    print("\rNew Client [" + str(client.getUUID()) + "] (" + str(len(clients)) + " connected client(s))")
    try:
        async for message in websocket:
            if not is_json(message): continue
            msg = json.loads(message)

            if 'origin' not in msg:
                continue

            if msg['origin'] == BROADCASTER:
                process.start() if not process.hasStarted else process.keepAlive()
                
            # Forward JSON to all Clients
            reply = json.dumps(msg)
            for client in set(clients):
                try:
                    await client.getSocket().send(reply)
                except:
                    # Connection to client has been lost or reset
                    clients.remove(client)
    except Exception:
        # Connection to client has been lost or reset
        clients.remove(client)
        print("\rConnection to Client [" + str(client.getUUID()) + "] lost or reset (" + str(len(clients)) + " connected client(s))")

print("### Starting Server ###\r\nHost: " + HOST + "\r\nPort: " + str(PORT))
listener = websockets.serve(on_message, HOST, PORT)
        
asyncio.get_event_loop().run_until_complete(listener)
asyncio.get_event_loop().run_forever()