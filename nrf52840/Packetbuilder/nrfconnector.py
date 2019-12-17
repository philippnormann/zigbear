import threading
from parse import *
import serial
import socket

class NrfConnector:
    def __init__(self, comPort):
        self.port = comPort
        self.baud = 115200
        self.timeout = 1
        self.ser = serial.Serial(self.port, baudrate=self.baud, timeout=self.timeout)
        self.wiresharkAddr = ("127.0.0.1", 5555)
        self.wiresharkSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, data):
        self.ser.write(data.encode())

    def sendPacket(self, data):
        self.wiresharkSock.sendto(bytearray.fromhex(data + "0000"), self.wiresharkAddr)
        self._send("send {}\n".format(data))

    def getChannel(self):
        self._send("channel\n")
        pass

    def setChannel(self, channel):
        self._send("channel {}\n".format(channel))
        pass

    def handle_data(self, data):
        receiveParsed = parse("received: power: {} lqi: {} data: {}", data)
        if receiveParsed:
            power = receiveParsed[0]
            lqi = receiveParsed[1]
            package = receiveParsed[2]
            #print(package)
            self.wiresharkSock.sendto(bytearray.fromhex(package + "0000"), self.wiresharkAddr)
        else:
            print("serial error: cannot parse {}".format(data))

    def read_from_port(self):
        buffer = ''
        while True:
            reading = self.ser.read_all()
            if reading:
                lines = (buffer + reading.decode()).split('\n')
                for line in lines[:-1]:
                    self.handle_data(line.strip())
                buffer = lines[-1]

    def start(self):
        thread = threading.Thread(target=self.read_from_port, args=(), daemon=True)
        thread.start()
