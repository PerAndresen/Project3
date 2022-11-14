import sys
import socket
import selectors
import types
import threading
import time

BROADCAST_PORT=33333
network = set()

def broadcastReceiver():
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    client.bind(("",BROADCAST_PORT))
    print("Listening for broadcast at ", client.getsockname())
    while True:
        data, addr = client.recvfrom(1024)
        print(data)
        data = data.decode('utf-8')
        print("Received message",data)
        dataMessage = data.split(' ')
        print("Received message",dataMessage)
        title = dataMessage[0]
        if title == 'HOST':
            host = dataMessage[1]
            port = int(dataMessage[3])
            name = "BOB"
            device = (host, port, name)
            network.add(device)
            print("Known devices: ", network)


broadcastReceiver()