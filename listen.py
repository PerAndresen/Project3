import socket
import forward_engine as fw


unitPort=fw.devicePort
global s
s = None
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
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
            print(input)
            splitWords = input.split(",")
            name=splitWords[0]
            type=splitWords[1]
            sender=splitWords[2]
            if type=="interest":
                package = fw.Interest(type=type,name=name, sender=sender)
            elif type=="data":
                package = fw.Data(content= splitWords[3])
                package.type=type
                package.name=name
                package.sender = sender
                print("Content received ", package.content)
            fw.inputHandler(package=package)
    finally:
        s.close()


def main():
    listener()
    

if __name__ == '__main__':
    main()