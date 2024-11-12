from time import sleep

import socketio
from socketio import SimpleClient

sock = socketio.Client()

@sock.event
def connect():
    print("I'm connected!")

@sock.event
def connect_error(data):
    print("The connection failed!")

@sock.event
def disconnect():
    print("I'm disconnected!")


sock.connect("http://127.0.0.1:5000/")

sock.emit("whereami_update", [{'team': 7, 'x':0, 'y':0}])

sock.disconnect()