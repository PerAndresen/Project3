import argparse
import random
import selectors
import socket
import time
import types

Dictionary = {
    'temp_high':'0000',
    'temp_low':'0001',
    'air_pressure':'0010',
    '/Local/Sensors/SensorWeather':'0100'
}

generators = {'speed': lambda: random.randint(40, 90),
                  'proximity': lambda: random.randint(1, 50),
                  'pressure': lambda: random.randint(20, 40),
                  'heartrate': lambda: random.randint(40, 120)}

def receive():
	print("Started reciever")
	receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	host = socket.gethostbyname(socket.gethostname())		
	receiver.bind((host, 33322))
	receiver.listen(3)
	receiver.setblocking(False)
	print("listening on ",host, 3302)
	while True:
		conn, _ = receiver.accept()
		data = conn.recv(1024)
		data = data.decode('utf-8')
		print("Data")
		if(data):
			receiver.send(b"Got the message")

receive()