import socket
import time
import os
import struct
import _thread
import selectors
import types

Dictionary = {'getd':'0000',  # get directory
			  'sendd':'0001', # send directory
			  'getf':'0010',  # get file
			  'sendf':'0011', # send file
			  'eof':'0100',   # end of file
			  'nofile':'0101',# no such file
			  'sensor':'1110',   # sensor
			  'quit':'1111',  # quit

			 }
# client codes:
def GetDirectory(sock):
	command = Dictionary['getd']
	sock.send(command.encode())
	Data=sock.recv(1024)
	command = Data[:4]
	FileList = Data[4:].decode()
	print('The files in the server are:')
	print(FileList.rstrip())

def GetFile(sock):
	filename = input('Please input the file you want:')
	command = Dictionary['getf']
	data = command+filename
	sock.send(data.encode())
	
	Data = sock.recv(1024)
	command = Data[:4].decode()
	if command == Dictionary['nofile']:
		print('No such file in the server!')
	else:
		with open (filename,'wb') as file_obj:
			print('Please waiting...')
			while True:				
				if command == Dictionary['eof']:
					break
				else:					
					data = Data[4:]
					if(data[-4:]==b'0100'): # 没有办法的办法
						break
					file_obj.write(data)	
				Data = sock.recv(1024)
				command = Data[:4].decode()
			print('File ' + filename + ' has been received.')

# server codes:
def SendDirectory(sock):
	FileList = os.listdir(os.getcwd())
	Directory = []
	for filename in FileList:
		if(~filename.rfind('.') and filename!='peer3.py'):
			Directory.append(filename)
	files = '    '
	for filename in Directory:				
		files += filename
		files += '\n    '
	DirEncode = files.encode()
	SELECT = b'0001'
	Data = SELECT+DirEncode
	sock.send(Data)

def SendFile(sock,name):
	FileList = os.listdir(os.getcwd())
	Directory = []
	for filename in FileList:
		if(~filename.rfind('.') and filename!='server.py'):
			Directory.append(filename)
	if name not in Directory:
		print('A wrong file name.')
		command = Dictionary['nofile']
		sock.send(command.encode())
	else:
		print('Transfering file ' + name + '.')
		with open (name,'rb') as file_obj:
			while True:
				block = file_obj.read(1020)
				if not block:
					command = Dictionary['eof'].encode()
					packet = command
					sock.send(packet)
					break;
				else:
					command = Dictionary['nop'].encode()
					packet = command+block
					sock.send(packet)
		print('Transfer the file completly.')

# client console:
def ClientConsole():
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.connect(('10.35.70.17',33303))
	print('==================================================')
	print('The peer is running as a client...')
	print('==================================================')
	print('Welcome to use the client(input help for help)')
	while True:
		operation = input(">>>")
		if operation=='getd':
			GetDirectory(s)
		elif operation=='getf':
			GetFile(s)
		elif operation=='quit':
			s.send(b'1111')
			s.close()
			break
		elif operation == 'sensor':
			os.system('python3 sensor.py')
			accept_sensor()
		elif operation=='help':
			print('getd: get the file list of the server.')
			print('getf: get file from the server.')
			print('quit: close the connection and quit.')
		else:
			print('wrong command, please input again.')
	print('The client has been logged out.')

# server console:
def ServerConsole(sock,addr):
	print('Server has been connected with %s:%s' %addr)
	while True:
		data = sock.recv(1024)
		command = data[:4].decode()
		# ~ print(command)
		if command==Dictionary['quit']:
			sock.close()
			break
		elif command==Dictionary['getd']:
			print('The client wants to get the directory of the files.')
			SendDirectory(sock)
		elif command==Dictionary['getf']:
			print('The client wants to get a file in the server.')
			name = data[4:].decode()
			SendFile(sock,name)
	print('Server has broken the connection with %s:%s' %addr)
	print('==================================================')
	
# multi threads:
def thread_client(threadName,ids):
	while True:
		try:
			ClientConsole()
		except ConnectionRefusedError:
			print('unable to connect the server.')
			continue

def thread_server(threadName,ids):
	s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	s.bind(('10.35.70.16',33302))
	s.listen(1)
	print('==================================================')
	print('The peer is running as a server...')
	print('==================================================')
	while True:
		print('Wait for a connection...')
		sock,addr = s.accept()
		ServerConsole(sock,addr)


####################### Accept sensor data


def accept_sensor():
	#selector = selectors.DefaultSelector()
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(('10.35.70.16', 33302))
	print("Socket bound to Port for sensor:", 33302)
	sock.listen()




# main thread:
# 创建两个线程
try:
   _thread.start_new_thread( thread_client, ("Thread-client",1))
   _thread.start_new_thread( thread_server, ("Thread-server",2))
except:
   print ("Error: unable to start thread")
while True:
	pass
