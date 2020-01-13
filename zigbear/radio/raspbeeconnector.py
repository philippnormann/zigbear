import serial
import math

from zigbear.radio.connector import Connector

class RaspbeeConnector(Connector):
    def __init__(self):
        super().__init__()
        self.port = '/dev/ttyS0'
        self.baud = 38400
        self.timeout = 0.1
        self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)

    def _send(self, data):
        l = math.floor(len(data) / 2) # TODO what if len(data) is not dividable by 2?
        self.ser.write(f'T:{l}:{data}'.encode())
        self.ser.flush()

    def _start(self):
        pass  # TODO

    def _close(self):
        pass  # TODO

    def _set_channel(self, channel):
        self.ser.write(f'S:{channel}'.encode())
        self.ser.flush()

    # TODO some function that call self.receive(package)
