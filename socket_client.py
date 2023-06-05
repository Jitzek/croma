#! /usr/bin/python3.7
import socket
import json
import websocket
import _thread

# set with socket_client.origin = 'value'
origin = ''

def on_message(ws, message):
    msg = json.loads(message)
    if (msg['origin'] == origin): return
    print('Message from ' + msg['origin'])
    print(msg['key'] + ': ' + msg['value'])

def on_error(ws, error):
    print('### An Error Occured', error, '###')

def on_close(ws):
    print("### Closed ###")

def on_open(ws):
    print("### Connected ###")

class SocketClient():
    connected = None
    def __init__(self, url):
        self.url = url
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.url,
            on_message = on_message,
            on_error = on_error,
            on_close = on_close,
            on_open = on_open)
        _thread.start_new_thread(self.ws.run_forever,())

    def retryConnection(self):
        self.ws = websocket.WebSocketApp(self.url,
            on_message = on_message,
            on_error = on_error,
            on_close = on_close,
            on_open = on_open)
        _thread.start_new_thread(self.ws.run_forever,())

    def isConnected(self):
        if self.connected: return self.connected
        # Ping Server
        try:
            self.ws.send('')
        except:
            self.connected = False
            return False
        self.connected = True
        return True

    def send(self, json):
        try:
            self.ws.send(json)
            self.connected = True
        except:
            self.connected = False
            pass
