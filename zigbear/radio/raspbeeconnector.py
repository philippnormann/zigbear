import sys
import math
import serial
from typing import List
from threading import Thread, currentThread

from zigbear.radio.connector import Connector


class RaspbeeConnector(Connector):
    def __init__(self, port='/dev/ttyS0', wireshark_host="127.0.0.1"):
        super().__init__(wireshark_host)
        self.port = port
        self.baud = 38400
        self.timeout = 0.1
        self.thread: Thread = None
        self.ser: serial.Serial = self.connect_raspbee()

    def connect_raspbee(self):
        ser = serial.Serial(
            port=self.port, baudrate=self.baud, timeout=self.timeout)
        inchar = ''
        while inchar != b'\n':
            ser.write(b'\n')
            ser.flush()
            inchar = ser.read(size=1)
        print('Connection to RaspBee established!')
        return ser

    def _set_channel(self, channel: str):
        self.ser.write(f'S:{channel.strip()}\n'.encode())
        self.ser.flush()

    def _send(self, data: str):
        # TODO: what if len(data) is not dividable by 2?
        l = math.floor(len(data) / 2)
        self.ser.write(f'T:{l}:{data}\n'.encode())
        self.ser.flush()

    def read_from_port(self):
        t = currentThread()
        while t.listen:
            line = self.ser.readline().decode().strip()
            args = line.split(':')
            cmd = args[0]
            if cmd is 'R':
                _, _length, _lqi, package = args
                self.receive(package)
            elif cmd is 'T':
                _, status = args
                print(f'\nTransmission status: {status}')
            elif cmd is 'S':
                _, channel, status = args
                print(f'\nSet channel {channel} status: {status}')

    def _start(self):
        if self.thread is None or (not self.thread.isAlive()):
            self.thread = Thread(target=self.read_from_port, args=(), daemon=True)
            self.thread.listen = True
            self.thread.start()
        else:
            print("Sniffer is already running")

    def _close(self):
        self.thread.listen = False
        self.thread.join()

