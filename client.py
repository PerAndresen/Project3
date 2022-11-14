import sys
import socket
import selectors
import types

sel = selectors.DefaultSelector()
messages = [b"My name is Bob", b"What is your name?"]
host, port, numm_conns = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
print(host,port)    
print(numm_conns)



def start_connections(host, port, numm_conns):
    server_addr = (host, port)
    for i in range(0, numm_conns):
        connid = i + 1
        print("Starting connection", connid, "to" ,server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        data = types.SimpleNamespace(
            connid = connid,
            msg_total = sum(len(m) for m in messages),
            recv_total = 0,
            messages = messages.copy(),
            outb =b"", 
        )
        sel.register(sock, events, data=data)

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print("Recieved", recv_data, "from connection ",data.connid)
            data.recv_total += len(recv_data)
        if not recv_data or data.recv_total == data.msg_total:
            print("Closing connection", data.connid)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print("Sending ",data.outb," to connection", data.connid)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]

start_connections(host,port,numm_conns)