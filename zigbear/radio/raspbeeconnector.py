import sys
import math
from serial import Serial
from typing import List
from threading import Thread

from zigbear.radio.connector import Connector


class RaspbeeConnector(Connector):
    def __init__(self, port='/dev/ttyS0', wireshark_host="127.0.0.1"):
        super().__init__(wireshark_host)
        self.port = port
        self.baud = 38400
        self.timeout = 0.1
        self.listen = False
        self.ser: Serial = self.connect_raspbee()
        self.thread: Thread = Thread(target=self.read_from_port, args=(), daemon=True)

    def connect_raspbee(self):
        ser = Serial(port=self.port, baudrate=self.baud, timeout=self.timeout)
        inchar = ''
        while inchar != b'\n':
            ser.write(b'\n')
            ser.flush()
            inchar = ser.read(size=1)
        print('Connection to RaspBee established!')
        return ser

    def _set_channel(self, channel: int):
        self.ser.write(f'S:{channel}\n'.encode())
        self.ser.flush()

    def _send(self, data: bytes):
        self.ser.write(f'T:{len(data)}:{data.hex()}\n'.encode())
        self.ser.flush()

    def read_from_port(self):
        while self.listen:
            line = self.ser.readline().decode().strip()
            args = line.split(':')
            cmd = args[0]
            if cmd is 'R':
                _, _length, _lqi, package_hex = args
                package_bytes = bytes.fromhex(package_hex)
                self.receive(package_bytes[:-2])
            elif cmd is 'T':
                _, status = args
                print(f'\nTransmission status: {status}')
            elif cmd is 'S':
                _, channel, status = args
                print(f'\nSet channel {channel} status: {status}')

    def _start(self):
        if self.thread is None or (not self.thread.isAlive()):
            self.listen = True
            self.thread.start()
        else:
            print("Sniffer is already running")

    def _close(self):
        self.listen = False
        self.thread.join()

