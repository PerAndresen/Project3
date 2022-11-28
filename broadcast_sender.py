import sys
import socket
import selectors
import types
import threading
import time
import forward_engine as fe

BROADCAST_PORT = 33339

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
