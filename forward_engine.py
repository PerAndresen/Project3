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
Dictionary = {
    'temp_high':'0000',
    'temp_low':'0001',
    'air_pressure':'0010',
    '/Local/Sensors/SensorWeather':'0100'
}
unitName="NewYork"

'''
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host = socket.gethostbyname(socket.gethostname())
s.bind((host, 33318))
s.listen(5) '''
#localSocket = s.dup()
#networkSocket = s.dup()

devicePort= 33338

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


class Pi:


    def __init__(self, host, port, name, target):
        self.host = host
        self.port = port
        self.name = name
        self.target = target
        self.network = set()



def inputHandler(package):
    #if content is interest
    if str(package.type) == "interest":
        #forwardInterest(package)
        forwardingInformationBase(package=package)
        checkSensors(package)
        checkContentStore(package=package)
    elif str(package.type) =="data":
        contentStore(package)
        #for key, nameOfDestination in pendingInterestTable.items():
          #if package.prefix == key:
           #     forwardData(package, nameOfDestination)

                    
def checkSensors(interest):
    print("Sending to sensors")
    splitWords = interest.name.split("/")
    if splitWords[1]==unitName:
        sensor=splitWords[2]
        sensorvalue = sensor1.Sensor.get_sensor(sensor)
        dataPackage = Data(sensorvalue)
        dataPackage.name = interest.name
        dataPackage.sender = interest.sender
        contentStore(dataPackage=dataPackage)


def forwardData(dataPackage, destination):
    print(destination)
    print(destination, "for data packet")
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[0]==destination:
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

'''
def listener():
    host = socket.gethostbyname(socket.gethostname())
    print("Listening on ", host, 33318)
    while True:
        conn, _ = s.accept()
        input = conn.recv(1024)
        input = input.decode('utf-8')
        print(input)
        splitWords = input.split(",")
        name=splitWords[0]
        type=splitWords[1]
        sender=splitWords[2]
        print(name,type)
        package = Package(name=name, type=type,sender=sender)
        print(package.type)
        inputHandler(package=package)
'''



def contentStore(dataPackage):
    print("Storing in content store")
    '''exists =False
    for name,data in list(cache.items()):
        if dataPackage.name == name:
            exists= True
            break
    if exists==False:'''
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
    #Keeping log of the wanted in buffer, triggers when receiving data.
    #If someone has requested it, we forward it to them
    #Sends required data

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

def createInterest(input):
    host = socket.gethostbyname(socket.gethostname())
    interest = Interest(type="interest",name=input,sender=host)
    print("Created interest")
    inputHandler(interest)


def ClientConsole():
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
            broadcast_sender.broadcast()
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
            createInterest(operation)       
    print('The client has been logged out.')

    
def main():
    #console = threading.Thread(target=ClientConsole())
    #broadcastOut = threading.Thread(target=broadcast_reciever())
    #broadcastIn = threading.Thread(target=broadcast_sender())
    #sensor = threading.Thread(target=sensor1())
    #sensor.start()
    #time.sleep(10)
    #console.start()
    os.system('python3 listen.py &')
    os.system('python3 sensor1.py &')
    console = threading.Thread(target=ClientConsole())
    console.start()
    

    #broadcastOut.start()
    #broadcastIn.start()



if __name__ == '__main__':
    main()

'''

def accept_sensor():
    #selector = selectors.DefaultSelector()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('10.35.70.16', 33302))
    print("Socket bound to Port for sensor:", 33302)
    sock.listen()
'''