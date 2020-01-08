import threading
from parse import *
import serial

from zigbear.radio.connector import Connector


class NrfConnector(Connector):
    def __init__(self, com_port):
        super().__init__()
        self.port = com_port
        self.baud = 115200
        self.timeout = 1
        self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)

    def __send(self, data):
        self.ser.write(data.encode())

    def _send(self, data):
        self.__send("send {}\n".format(data))

    def _set_channel(self, channel):
        self.__send("channel {}\n".format(channel))

    def handle_data(self, data):
        receiveParsed = parse("received: power: {} lqi: {} data: {}", data)
        if receiveParsed:
            power = receiveParsed[0]
            lqi = receiveParsed[1]
            package = receiveParsed[2]
            self.receive(package)
        else:
            pass
            #print("serial error: cannot parse {}".format(data))

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
