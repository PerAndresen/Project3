#!/usr/bin/env python3

import argparse
import random
import selectors
import socket
import time
import types
import pandas as pd


weathers = pd.read_csv("climate.csv")
tempHigh = weathers.iloc[:,1]
tempAvg = weathers.iloc[:,2]
tempLow = weathers.iloc[:,3]
DewAvg = weathers.iloc[:,5]
HumidAvg = weathers.iloc[:,8]
SeaLevelAvg = weathers.iloc[:,11]
VisibilityAvg = weathers.iloc[:,14]
WindAvg = weathers.iloc[:,17]



class Sensor:
    # Map sensor types to random value generator functions
    generators = {'speed': lambda: random.randint(40, 90),
                  'proximity': lambda: random.randint(1, 50),
                  'pressure': lambda: random.randint(20, 40),
                  'heartrate': lambda: random.randint(40, 120)}

    dictionary = {
        'TempHigh': tempHigh,
        'TempAvg': tempAvg,
        'TempLow': tempLow,
        'DewAvg': DewAvg,
        'HumidAvg': HumidAvg,
        'SeaLevel': SeaLevelAvg,
        'VisibilityAvg': VisibilityAvg,
        'WindAvg': WindAvg
    }

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.selector = selectors.DefaultSelector()
        self.finished = False

    def start_connections(self, num_conns, messages):
        server_addr = (self.host, self.port)
        for i in range(0, num_conns):
            conn_id = i + 1
            print(f'Starting connection #{conn_id} to {server_addr}')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(False)
            sock.connect_ex(server_addr)
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
            data = types.SimpleNamespace(conn_id=conn_id,
                                         msg_total=sum(len(m) for m in messages),
                                         recv_total=0,
                                         messages=list(messages),
                                         out_bytes='')
            self.selector.register(sock, events, data=data)

    def service_connection(self, key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = sock.recv(1024)
            if recv_data:
                data.recv_total += len(recv_data)
        elif mask & selectors.EVENT_WRITE:
            if not data.out_bytes and data.messages:
                data.out_bytes = data.messages.pop(0)
                index = random.randint(1, 1320)
                val1 = Sensor.dictionary.get('TempHigh')[index]
                val2 = Sensor.dictionary.get('TempAvg')[index]
                val3 = Sensor.dictionary.get('TempLow')[index]
                val4 = Sensor.dictionary.get('DewAvg')[index]
                val5 = Sensor.dictionary.get('HumidAvg')[index]
                val6 = Sensor.dictionary.get('SeaLevel')[index]
                val7 = Sensor.dictionary.get('VisibilityAvg')[index]
                val8 = Sensor.dictionary.get('WindAvg')[index]
                valstr = f'{"TempHigh"} {val1}  {"TempAvg"} {val2}  {"TempLow"} {val3}  {"DewAvg"} {val4}  ' \
                         f'{"HumidAvg"} {val5}  {"SeaLevel"} {val6}  {"VisibilityAvg"} {val7}  {"WindAvg"} {val8} '
                data.messages.append(valstr.encode('utf-8'))

            if data.out_bytes:
                print(data.out_bytes.decode('utf-8'))
                sent = sock.send(data.out_bytes)
                data.out_bytes = data.out_bytes[sent:]
                time.sleep(5)
        return self.finished

    def run(self):
        while not self.finished:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                try:
                    self.service_connection(key, mask)
                except ConnectionRefusedError:
                    addr = f'{{Host:{self.host}, Port:{self.port}}}'
                    print(f'Node with address {addr} not found')
                    break


def main():
    port_table = {'VehiclePort': 33317}  # Hardcoded port table for testing
    port = port_table['VehiclePort']     # The port used by the server
    initial_message = "sensor Data as follows:"
    byte_messages = [initial_message.encode('UTF-8')]

    # The server's hostname or IP address
    host = socket.gethostbyname(socket.gethostname())
    mySensor = Sensor(host, port)
    mySensor.start_connections(1, byte_messages)
    mySensor.run()


if __name__ == '__main__':
    main()
