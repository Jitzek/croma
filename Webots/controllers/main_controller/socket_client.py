#! /usr/bin/python3.7
import socket
import json
import websocket
import _thread
import time

# set with socket_client.origin = 'value'
origin = ''

def on_message(ws, message):
    msg = json.loads(message)
    if (msg['origin'] == origin): return
    print('Message from ' + msg['origin'])
    print(msg['key'] + ': ' + msg['value'])

def on_error(ws, error):
    #print('### An Error Occured', error, '###')
    pass

def on_close(ws):
    #print("### Closed ###")
    pass

def on_open(ws):
    print("### Connected ###")

class SocketClient():
    CONNECTION_RETRY_TIMEOUT = 512
    connection_retry_count = CONNECTION_RETRY_TIMEOUT

    connected = None
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.url = 'ws://{}:{}'.format(host, port)

    def connect(self):
        if self.connection_retry_count < self.CONNECTION_RETRY_TIMEOUT:
            self.connection_retry_count += 1
            return
        self.connection_retry_count = 0
        websocket.enableTrace(False)
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

    def send(self, json_string):
        print(json_string)
        try:
            self.ws.send(json_string)
            self.connected = True
        except Exception as e:
            self.connected = False
            pass
