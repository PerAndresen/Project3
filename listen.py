import socket
import types
import forward_engine as fw
import sys
import selectors

sel = selectors.DefaultSelector()

unitPort=int(sys.argv[1])
global s
s = None
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
host = socket.gethostbyname(socket.gethostname())
s.bind((host, unitPort))
s.listen(5)
s.setblocking(False)
sel.register(s,selectors.EVENT_READ,data=None)


def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print(f"Accepted connection from {addr}")
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)  # Should be ready to read
        if recv_data:
            listener(recv_data)
        else:
            print(f"Closing connection to {data.addr}")
            sel.unregister(sock)
            sock.close()


def listener(input):
    host = socket.gethostbyname(socket.gethostname())
    print("Listening on ", host, unitPort)
    while True:
            #conn, _ = s.accept()
            #input = conn.recv(1024)
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
'''
finally:
s.shutdown()
s.close()
'''

try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key,mask)
except:
     print("Caught keyboard interrupt, exiting")
finally:
    sel.close()

'''
def main():
    listener()
    

if __name__ == '__main__':
    main()
'''