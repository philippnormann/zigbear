import threading
from PyCRC.CRC16Kermit import CRC16Kermit
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

    def get_CRC(self, package):
        packageBytes = bytes.fromhex(package)
        return hex(CRC16Kermit().calculate(packageBytes))[2:].zfill(4)

    def handle_data(self, data):
        receiveParsed = parse("received: power: {} lqi: {} data: {}", data)
        if receiveParsed:
            power = receiveParsed[0]
            lqi = receiveParsed[1]
            package = receiveParsed[2]
            #print(package)
            packageArray = bytearray.fromhex(package)
            self.wiresharkSock.sendto(bytearray.fromhex(package + self.get_CRC(package)), self.wiresharkAddr)
        else:
            print("serial error: cannot parse {}".format(data))

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

    def start(self):
        if (not hasattr(self, 'thread')) or (not self.thread.isAlive()):
            self.thread = threading.Thread(target=self.read_from_port, args=(), daemon=True)
            self.thread.start()
        else:
            print("Sniffer is already running")

    def stop(self):
        self.thread.continue_sniffing = False
        self.thread.join()
