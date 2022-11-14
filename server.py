import sys
import socket
import selectors
import types
import threading
import time

BROADCAST_PORT = 3333
PUBLIC_PORT = 3330
sel = selectors.DefaultSelector()



class Pi:


	def __init__(self, host, port, name, target):
		self.host = host
		self.port = port
		self.name = name
		self.target = target
		self.network = set()
		
					
	def accept_wrapper(sock):
		conn, addr = sock.accept()
		print("Accepted connection from", addr)
		conn.setblocking(False)
		data = types.SimpleNamespace(addr=addr, inb=b"", outb=b"")
		events = selectors.EVENT_READ | selectors.EVENT_WRITE
		sel.register(conn,events, data =data)

	def service_connection(key, mask):
		sock = key.fileobj
		data = key.data
		if mask & selectors.EVENT_READ:
			recv_data = sock.recv(1024)
			if recv_data:
				data.outb += recv_data
				recieved = recv_data.decode('utf-8')
				print('Received', received)
				#STORE IN CACHE
				#PRINT TO FILE
				f = open("cache.txt", "a")
				f.write(recieved)
				#HERE WE CAN DECIDE ON THE DIFFERENT SENSORS
			else:
				print("Closing connection to ",data.addr)
				sel.unregister(sock)
				sock.close()
		if mask & selectors.EVENT_WRITE:
			if data.outb:
				print("Echoing ",data.outb," to ",data.addr)
				sent = sock.send(data.outb)
				data.outb = data.outb[sent:]

	def broadcast(self):
		print("Broadcasting")
		broad = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		broad.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		broad.settimeout(0.5)
		message = f'HOST {self.host} PORT {BROADCAST_PORT} NAME {self.name}'.encode('utf-8')
		while True:
			broad.sendto(message, ('<broadcast>',BROADCAST_PORT))
			time.sleep(10)

	def broadcastReceiver(self):
		client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
		client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		client.bind(("",BROADCAST_PORT))
		while True:
			data, _ = client.recvfrom(1024)
			data = data.decode('utf-8')
			dataMessage = data.split(' ')
			print(dataMessage)
			title = dataMessage[0]
			if title == 'HOST':
				host = dataMessage[1]
				port = int(dataMessage[3])
				name = dataMessage[5]
				device = (host, port, name)
				if ndn != (self.host, self.port, self.name):
					self.network.add(device)
					print("Known devices: ", self.network)

	def receive(self):
		print("Started reciever")
		receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		receiver.bind((self.host, self.port))
		receiver.listen(10)
		print("listening on ",self.host, self.port)
		while True:
			conn, _ = receiver.accept()
			data = conn.recv(1024)
			data = data.decode('utf-8')
			print(data)
			conn.close()
			time.sleep(1)
	
	def sender(self):
		print("Waiting for input")
		user_input = input("Some input please: ")
		print(user_input)
		sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		target = "10.35.70.16"
		port = 3331
		sender.connect((target, port))
		sender.send(user_input.encode())
		sender.close()	


def main():
	target = sys.argv
	hostname = socket.gethostname()
	host = socket.gethostbyname(hostname)
	unit = Pi(host, PUBLIC_PORT, "Per", target)
	broadcast = threading.Thread(target=unit.broadcast)
	receiver = threading.Thread(target=unit.receive)
	sender = threading.Thread(target=unit.sender)
	broadcastReceiver = threading.Thread(target=unit.broadcastReceiver)
	broadcast.start()
	#receiver.start()
	broadcastReceiver.start()
	#sender.start()
	try:
		while True:
			events = sel.select(timeout=None)
			for key, mask in events:
				if key.data is None:
					accept_wrapper(key.fileobj)
				else:
					service_connection(key, mask)
	except KeyboardInterrupt:
		print("Caught keyboard interrupt, exiting")
	finally:
		sel.close()


if __name__ == '__main__':
	main()
