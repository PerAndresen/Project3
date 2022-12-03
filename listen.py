import socket
import forward_engine as fw
import sys


unitPort=int(sys.argv[1])
global s
s = None
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
host = socket.gethostbyname(socket.gethostname())
s.bind((host, unitPort))
s.listen(5)

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


def main():
    listener()
    

if __name__ == '__main__':
    main()