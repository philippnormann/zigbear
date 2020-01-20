import math
import threading
import time

import serial
from parse import *

from zigbear.radio.connector import Connector


class NrfConnector(Connector):
    def __init__(self, com_port):
        super().__init__()
        self.port = com_port
        self.baud = 115200
        self.timeout = 1
        self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)

    def __send(self, data: str):
        c = math.ceil(len(data) / 80)
        for i in range(c):
            self.ser.write(data[i * 80:(i * 80) + 80].encode())
            self.ser.flush()
            time.sleep(0.01)

    def _send(self, data: bytes):
        self.__send(f"send {data.hex()}\n")

    def _set_channel(self, channel: int):
        self.__send(f"channel {channel}\n")

    def handle_data(self, data: str):
        receiveParsed = parse("received: power: {} lqi: {} data: {}", data)
        if receiveParsed:
            _power = receiveParsed[0]
            _lqi = receiveParsed[1]
            package_hex = receiveParsed[2]
            package_bytes = bytes.fromhex(package_hex)
            self.receive(package_bytes)
        else:
            pass
            # print("serial error: cannot parse {}".format(data))

    def read_from_port(self):
        buffer = ''
        t = threading.currentThread()
        while getattr(t, "continue_sniffing", True):
            reading = self.ser.read_all()
            if reading:
                lines = (buffer + reading.decode()).split('\n')
                for line in lines[:-1]:
                    self.handle_data(line.strip())
                buffer = lines[-1]

    def _start(self):
        if (not hasattr(self, 'thread')) or (not self.thread.isAlive()):
            self.thread = threading.Thread(target=self.read_from_port, args=(), daemon=True)
            self.thread.start()
        else:
            print("Sniffer is already running")

    def _close(self):
        self.thread.continue_sniffing = False
        self.thread.join()
