import sys
import socket
import selectors
import types
import threading
import time
import csv

BROADCAST_PORT=33339

class Device:

    def __init__(self, host, port, name):
        self.host=host
        self.port=port
        self.name=name

    def __str__(self):
        return str(self.host)+","+str(self.port)+","+str(self.name)


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
        title = dataMessage[0]
        if title == 'GROUP8':
            print("Received message",dataMessage)
            host = dataMessage[2]
            port = int(dataMessage[4])
            name = dataMessage[6]
            print(name)
            device = Device(host, port, name)
            print(device)
            saveNetworks(device)

def saveNetworks(device):
    print(device)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    exists = False
    for row in networks:
        print("Row 0", row[0])
        print(device.host)
        #if row[1] == device.port:
        #    print('exists')
        #    exists = True
        #    break
        #Hostname IP already exists
        if row[2] == device.name:
            print('exists')
            exists = True
            break
            #Name already exists        
    if exists != True:
        f = open("networks.csv", "a")
        f.write(device.__str__()+"\n")
        f.close()
        print("Network saved")

