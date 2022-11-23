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


cache = {}
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
        dataname = package.name
        sender = package.sender
        forwardingInformationBase(dataname,sender)
        checkContentStore(dataname,sender)
        checkSensors(package)
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
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[2]==destination:
            target=row[0]
            port=row[1]
            package = Data(destination,content)
            print("Forwarding data to requested destination")
            forward.connect((target,port))
            forward.send(package.encode())
            forward.close()


def forwardInterest(name, parameters):
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if row[2]==name:
            target=row[0]
            port=row[1]
            package = Interest(name,parameters)
            print("Forwarding interest to requested destination")
            forward.connect((target,port))
            forward.send(package.encode())
            forward.close()


def listener(Pi):
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.bind ((Pi.host, Pi.port))
    listener.listen(5)
    print("Listening on ", Pi.host, Pi.port)
    while True:
        conn, _ = listener.accept()
        input = conn.recv(1024)
        input = input.decode('utf-8')
        inputHandler(input)


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

def forwardingInformationBase(name, parameters):
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    for row in networks:
        if name == row[2]:
            forwardInterest(name, parameters)
    #Check if there is a pending interesent with this data

def createInterest(input):
    interest = Interest(type="interest",name=input,sender="BOB")
    interest.type="interest"
    print("Created interest")
    inputHandler(interest)


def ClientConsole():
    print('==================================================')
    print('Your device is now running')
    print('==================================================')
    print('Welcome to the NDN network(input help for help)')
    while True:
        operation = input(">>>")
        if operation=='/Local/Sensors':
            #GetListOfSensors()
            print("Sensors")
        elif operation=='/Local/Sensors/SensorWeather':
            createInterest(operation)
        elif operation=='/Local/Sensors/WindSpeed':
            #GetWindSpeed()
            print("Windspeed")    
        elif operation=='/Local/Sensors/WindDirection':
            #GetWindDirection()    import sensor1

            break
        elif operation=='help':
            print('/Sensors: Get list of sensors.')
            print('getf: get file from the server.')
            print('quit: close the connection and quit.')
        else:
            createInterest(operation)
            print('Checking the internet for this query')
    print('The client has been logged out.')

    
def main():
    console = threading.Thread(target=ClientConsole())
    broadcastOut = threading.Thread(target=broadcast_reciever())
    broadcastIn = threading.Thread(target=broadcast_sender())
    #sensor = threading.Thread(target=sensor1())
    #sensor.start()
    #time.sleep(10)
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