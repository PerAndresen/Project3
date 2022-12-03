This is a group assignment done for the course Scalable Computing. Our task was to implement a peer-2-peer network with aspects of Content Centric Networking. We chose to implement our own interpretation of a Named Data Networking(NDN) architecture. In this readMe. I will go through the concepts we implemented and what the actual implementation looks like. At the end you will be shown how to run the project.

This project was completed by:

Xiaohan Shi: 22301413
Per Bergsjø Andresen: 22300432
Xinhe Chen: 22300064
Shuotan Chao: 22324118

NDN offers two different types of packets. Data and Interest. For this to be implemented we created three different classes, Package, Data and Interest. Data and Interest are subtypes of the superclass Package. 
```
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
```

We also have a method for creatingInterest. Which takes input from the commandline. E.g

/NewYork/Temp

This creates an interest package which gets sent to the inputhandler. Where it later gets forwarded to the correct destination.

Each package gets handed differently in our inputHandler. The method gets called every time the local user creates an interest or recieves packages from ohter devices. This checks what type of package is incoming, and sends it to different destinations accordingly.

```
def inputHandler(package,city):
    if str(package.type) == "interest":
        forwardingInformationBase(package=package)
        checkSensors(interest=package,city=city)
        checkContentStore(package=package)
    elif str(package.type) =="data":
        contentStore(package)
```

Interest packages gets sent to a Forward Information Base. This stores the name of the package and who sends it. It also keeps record of if the interest has been forwarded to other devices or not. The information gets stored in a dictionary that empties for each session of the device.

```
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
```
After being sent to the FIB, the Interest gets sent to check the sensors of the local device that is handling the package. Sensor1 is a file that runs in the background for the device when the project is run. This method checks if the interest package has the route/name of the local device, if it is correct it checks it sensors. Then it creates a datapackage which is stored in the ContentStore.
```
def checkSensors(interest,city):
    print("Sending to sensors",interest.name)
    print(interest.name)
    splitWords = interest.name.split("/")
    print(splitWords[1])
    if city==splitWords[1]:
        sensor=splitWords[2]
        sensorvalue = sensor1.Sensor.get_sensor(sensor)
        print(sensorvalue)
        dataPackage = Data(content=sensorvalue)
        dataPackage.name = interest.name
        dataPackage.sender = interest.sender
        print(dataPackage.content)
        contentStore(dataPackage=dataPackage)
```
If the interest package's destination is not this device, it checks the contentstore of its device. It checks if it is stored a Data package from another device locally, which helds the information the interest is looking for. 

```
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
```

If it finds the data stored in the content stored, this data gets forwarded to the sender of the interest package.
```
def forwardData(dataPackage, destination):
    print(destination)
    print(destination, "for data packet")
    forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    forward.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
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
```

Our project also has a method for forwarding interest, which is called in the FIB, if the interest has not already been forwarded.
```
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
```

If the input handler recieves a Data packet. It stores the content in the contentstore.

```
def contentStore(dataPackage):
    print("Storing in content store")
    name = dataPackage.name
    data = dataPackage.content 
    newContent = {name:data}
    print(newContent)
    cache.update(newContent)
    print("Content saved")
```

Our project has a listener and two broadcast methods. The listener waits for incoming packages and creates packages locally of them. The broadcast methods is runned for either sending broadcasts or recieving them. 
```
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
            break


def broadcast(port,name):
    print("Broadcasting")
    broad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broad.settimeout(0.5)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    print(host)
    message = f'GROUP8 HOST {host} PORT {port} NAME {name}'.encode('utf-8')    
    broad.sendto(message, ('10.35.70.255',BROADCAST_PORT))
    print("Message sent!", message)
    time.sleep(5)

def listener():
    try:
        host = socket.gethostbyname(socket.gethostname())
        print("Listening on ", host, unitPort)
        while True:
            conn, _ = s.accept()
            input = conn.recv(1024)
            input = input.decode('utf-8')
            splitWords = input.split(",")
            name=splitWords[0]
            print("Name: ",name)
            type=splitWords[1]
            print(type)
            sender=splitWords[2]
            if type=="interest":
                package = fw.Interest(type=type,name=name, sender=sender)
            elif type=="data":
                package = fw.Data(content= splitWords[3])
                package.type=type
                package.name=name
                package.sender = sender
                print("Content received ", package.content)
            print(package)
            split = name.split("/")
            fw.inputHandler(package=package,city=split[1])
    finally:
        s.shutdown()
        s.close()
```

# How to run the project

For running the project you need to open two seperate terminals. And run the commands, in each.

```
python3 forward_engine.py NewYork 33345
```

```
python3 forward_engine.py Tokyo 33355
```

For each device you will have a separate client. For this devices to communicate you have to start broadcasting their names and routes. First one has to send and the other recieve, then swap. 

Broadcast/Recieve 

Broadcast/Send

After this is done successfully the networks will be saved. Then you can send an interest package from one device. From tokyo you can ask about the temperature in NewYork. 

/NewYork/Temp

That is it for our project. Hope you like it. 