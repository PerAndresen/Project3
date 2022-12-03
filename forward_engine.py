import argparse
import sys
import socket
import threading
import types
import csv
import os
import broadcast_reciever
import broadcast_sender
import sensor1
import time


cache = {
    '/NewYork/Temperature':'80'
}
informationBase= {
    '/NewYork/Sensor':'0'
}
pendingInterestTable = {}


#Tried implementing this to create a global object that can be accessed by the listener.
class Unit:

    def __init__(self,city, port):
        self.city=city
        self.port=port
    
    def __str__(self):
        return self.city + self.port

thisUnit=Unit(city="",port=0)
sensorPort=33333

class Package:

    def __init__(self, type, name,sender):
        self.type=type
        self.name=name
        self.sender=sender
    
    def __str__(self):
        return self.type
        
class Interest(Package):
    pass

        

class Data(Package):

    def __init__(self, content):
        self.content = content
        #self.signature = signature


def inputHandler(package,city):
    #if content is interest
    if str(package.type) == "interest":
        forwardingInformationBase(package=package)
        checkSensors(interest=package,city=city)
        checkContentStore(package=package)
    elif str(package.type) =="data":
        contentStore(package)

                    
def checkSensors(interest,city):
    print("Sending to sensors",interest.name)
    print(interest.name)
    splitWords = interest.name.split("/")
    print(splitWords[1])
    #print(thisUnit.city)
    '''hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[0]==host:
            cityname=row[2]'''
    if city==splitWords[1]:
        sensor=splitWords[2]
        sensorvalue = sensor1.Sensor.get_sensor(sensor)
        print(sensorvalue)
        dataPackage = Data(content=sensorvalue)
        dataPackage.name = interest.name
        dataPackage.sender = interest.sender
        print(dataPackage.content)
        contentStore(dataPackage=dataPackage)


def forwardData(dataPackage, destination):
    print(destination)
    print(destination, "for data packet")
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #forward.setblocking(False)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[2]==destination:
            target=row[0]
            port=int(row[1])
            print(target,port)
            print("Forwarding data to requested destination")
            forward.connect((target,port))
            message = f'{dataPackage.name},{dataPackage.type},{dataPackage.sender},{dataPackage.content}'.encode('utf-8')
            forward.send(message)
            forward.close()


def forwardInterest(package):
    words= package.name.split("/")
    networkName= words[1]
    print(networkName)
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #forward.setblocking(False)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[2]==networkName:
            target=row[0]
            port=int(row[1])
            print("Forwarding interest to requested destination")
            forward.connect((target,port))
            message = f'{package.name},{package.type},{package.sender}'.encode('utf-8')
            print(message)
            forward.send(message)
            forward.close()


def contentStore(dataPackage):
    print("Storing in content store")
    name = dataPackage.name
    data = dataPackage.content 
    newContent = {name:data}
    print(newContent)
    cache.update(newContent)
    print("Content saved")

def checkContentStore(package):
    print("Checking content store")
    for name, data in list(cache.items()):
        if package.name == name:
            print("Found in contentstore")
            dataPackage= Data(content=data)
            dataPackage.name=name
            dataPackage.type="data"
            dataPackage.sender=package.sender
            print(package.sender)
            forwardData(dataPackage, package.sender)
        


def checkInterestTable(prefix, sender, content):
    for query, author in pendingInterestTable:
        if prefix == query and author==sender:
            forwardData(content, author)

def forwardingInformationBase(package):
    print("Checking informationbase")
    exists=False
    for interest, value in list(informationBase.items()):
        if package.name == interest:
            exists=True
            if value=='0':
                forwardInterest(package)
                informationBase[interest]='1'
            elif value=='1':
                print(interest, "Already forwarded")
    
    if exists== False:
        name = package.name
        newInterest={name:'1'}
        print(newInterest)
        informationBase.update(newInterest)
        forwardInterest(package)

def createInterest(input,city):
    #host = socket.gethostbyname(socket.gethostname())
    interest = Interest(type="interest",name=input,sender=city)
    print("Created interest")
    inputHandler(interest,city)


def ClientConsole(city):

    #listener()
    print('==================================================')
    print('Your device is now running')
    print('==================================================')
    print('Welcome to the NDN network(input help for help)')
    while True:
        operation = input(">>>")
        if operation=='/Local/Sensors':
            print("Sensors")
        elif operation=='/Local/Sensors/SensorWeather':
            createInterest(operation)
        elif operation=='/Local/Sensors/WindSpeed':
            print("Windspeed")
        elif operation == 'Broadcast/Recieve':
            broadcast_reciever.broadcastReceiver()
        elif operation == 'Broadcast/Send':
            broadcast_sender.broadcast(thisUnit.port, city)
        elif operation=='quit':
            break
        elif operation=='listen':
            print("Listening")
        elif operation=='help':
            print('/Sensors: Get list of sensors.')
            print('getf: get file from the server.')
            print('quit: close the connection and quit.')
        elif operation =='data':
            package = Package(type="interest",name="/NewYork/Temp", sender="Bob")
            checkSensors(package=package)
        else:
            createInterest(operation,city)       
    print('The client has been logged out.')

    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--city", required=True)
    parser.add_argument("-p", "--port", required=True)
    args = parser.parse_args()
    city = args.city
    thisUnit.port = int(args.port)
    os.system('python3 listen.py %d &'%thisUnit.port)
    os.system('python3 sensor1.py &')
    console = threading.Thread(target=ClientConsole(city))
    console.start()

if __name__ == '__main__':
    main()
