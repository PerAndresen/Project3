import sys
import socket
import selectors
import types
import threading
import time

BROADCAST_PORT = 33333

def broadcast():
    print("Broadcasting")
    broad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broad.settimeout(0.5)
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    print(host)
    message = f'HOST {host} PORT {BROADCAST_PORT} NAME BOB'.encode('utf-8')
    while True:
        broad.sendto(message, ('10.35.70.255',BROADCAST_PORT))
        print("Message sent!")
        time.sleep(100)




broadcast()