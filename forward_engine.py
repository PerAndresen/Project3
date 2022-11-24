import sys
import socket
import threading
import types
import csv
import os
import broadcast_reciever
import broadcast_sender
#import sensor1
import time


cache = {}
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


class Package:

    def __init__(self, type, name,sender):
        self.type=type
        self.name=name
        self.sender=sender
    
    def __str__(self):
        return self.type
        
class Interest(Package):
    pass

        #self.parameters = parameters

        

class Data(Package):

    def __init__(self, content, signature):
        self.content = content
        self.signature = signature


class Pi:


    def __init__(self, host, port, name, target):
        self.host = host
        self.port = port
        self.name = name
        self.target = target
        self.network = set()



def inputHandler(package):
    print(package.type)
    print(type(package.type))
    #if content is interest
    if str(package.type) == "interest":
        print(package.type)
        #forwardInterest(package)
        forwardingInformationBase(package=package)
        #checkContentStore(dataname,sender)
        #checkSensors(package)
    elif str(package.type) =="data":
        dataname = package.name
        content = package.content
        #signature = package.signature host = socket.gethostbyname(socket.gethostname())
        #checkInterestTable(dataname, parameters)
        contentStore(dataname, content)
        for key, nameOfDestination in pendingInterestTable.items():
            if package.prefix == key:
                forwardData(package, nameOfDestination)

                    
def checkSensors(package):
    print("Sending to sensors")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    print('HostIP',host)
    #sock.bind((host,33378))
    message= str(package)
    sock.connect((host,33322))
    sock.send(message.encode("utf-8"))
    while True:
        conn, _ = sock.accept()
        dataFromSensor= conn.recv(1024)
        #print(dataFromSensor.decode())
        return dataFromSensor.decode()



def forwardData(content, destination):
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    networks = csv.reader(open("networks.csv","wr"),delimiter=",")
    for row in networks:
        if row[2]==destination:
            target=row[0]
            port=int(row[1])
            print(target,port)
            package = Data(destination,content)
            print("Forwarding data to requested destination")
            forward.connect((target,port))
            forward.send(package.encode())
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
            print(target,port)
            print("Forwarding interest to requested destination")
            forward.connect((target,port))
            message = f'{package.name},{package.type},{package.sender}'.encode('utf-8')
            print(message)
            forward.send(message)
            forward.close()


def listener(sock):
    host = socket.gethostbyname(socket.gethostname())
    print("Listening on ", host, 33318)
    while True:
        conn, _ = sock.accept()
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


def contentStore(name, data):
    if name not in cache:
        cache[name]=data
    else:
        return
    #Where all the data is keptelif operation=='/Local/Sensors/WindSpeed':
    #Database for keeping the content.

def checkContentStore(interest, sender):
    for key, data in cache.items():
        if interest == key:
            print("Found in cache")
            forwardData(data, sender)


def checkInterestTable(prefix, sender, content):
    for query, author in pendingInterestTable:
        if prefix == query and author==sender:
            forwardData(content, author)
    #Keeping log of the wanted in buffer, triggers when receiving data.
    #If someone has requested it, we forward it to them
    #Sends required data

def forwardingInformationBase(package):
    print("Checking informationbase")
    for interest, value in informationBase.items():
        if package.name == interest:
            if value=='0':
                forwardInterest(package)
            if value=='1':
                print(interest, "Already forwarded")
    
        
    '''informationBase = csv.reader(open("forwardDB.csv", "r"), delimiter=",")
    exists = False
    for row in informationBase:
        if row[0]==package.name:
            exists = True
            f = open("forwardDB.csv","w")
            f.write(package.name+",0"+"\n")
            f.close()
            if row[1]=="0":
                forwardInterest(package=package)
            elif row[1]=="1":
                break
    if exists != True:
        f = open("forwardDB.csv","a")
        f.write(package.name+",0"+"\n")
        f.close()'''
    #Check if there is a pending interest with this data

def createInterest(input):
    host = socket.gethostbyname(socket.gethostname())
    interest = Interest(type="interest",name=input,sender=host)
    print("Created interest")
    inputHandler(interest)


def ClientConsole():
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host = socket.gethostbyname(socket.gethostname())
    s.bind((host, 33318))
    s.listen(5)
    #listener()
    print('==================================================')
    print('Your device is now running')
    print('==================================================')
    print('Welcome to the NDN network(input help for help)')
    while True:
        operation = input(">>>")
        if operation=='/Local/Sensors':
            #GetListOfSensors()
            os.system('python3 sensor.py --sensortype speed')
            print("Sensors")
        elif operation=='/Local/Sensors/SensorWeather':
            createInterest(operation)
        elif operation=='/Local/Sensors/WindSpeed':
            #GetWindSpeed()
            print("Windspeed")
        elif operation == 'Broadcast/Recieve':
            broadcast_reciever.broadcastReceiver()
        elif operation == 'Broadcast/Send':
            broadcast_sender.broadcast()
        elif operation=='quit':
            #GetWindDirection()    import sensor1
            break
        elif operation=='listen':
            listener(s)
        elif operation=='help':
            print('/Sensors: Get list of sensors.')
            print('getf: get file from the server.')
            print('quit: close the connection and quit.')
        else:
            createInterest(operation)
            print('Checking the internet for this query')
    print('The client has been logged out.')
    s.close()

    
def main():
    #console = threading.Thread(target=ClientConsole())
    #broadcastOut = threading.Thread(target=broadcast_reciever())
    #broadcastIn = threading.Thread(target=broadcast_sender())
    #sensor = threading.Thread(target=sensor1())
    #sensor.start()
    #time.sleep(10)
    #console.start()
    ClientConsole()
    
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