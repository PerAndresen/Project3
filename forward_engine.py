import sys
import socket
import types

cache = {}
pendingInterestTable = {}

class State:

    __init__(self):


def inputHandler(content):
    #if content is interest
    if content.type == "interest":
        prefix = content.route
        sender = content.sender
        pendingInterestTable(prefix, sender)
        forwardingInformationBase(content.prefix)
        checkContentStore(content.interest)
    elif content.type =="data":
        contentStore(content.name, content.data)
        if content.type == data:
            for key, nameOfDestination in pendingInterestTable.items():
                if content.prefix = key:
                    forwardData(content, nameOfDestination)
    

    

    #if content is data

def contentStore(name, data):
    if name not in cache:
        cache[name]=data
    else:
        return null
    #Where all the data is kept
    #Database for keeping the content.

def checkContentStore(interest):
    for key, data in cache.items():
        if interest = key:
            forwardData(data, interest.source)


def pendingInterestTable(prefix, requestingFace):
    #Keeping log of the wanted in buffer, triggers when receiving data.

    #If someone has requested it, we forward it to them
    #Sends required data


def forwardingInformationBase(prefix, faceList):
    networks = csv.reader(open("networks.csv","r"),delimiter=",")
    exists = False
    for row in networks:

    while True:
        
            #Check if there is a pending interesent with this data.
            


