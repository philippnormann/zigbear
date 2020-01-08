import socket
from abc import abstractmethod
from PyCRC.CRC16Kermit import CRC16Kermit


class Connector:
    def __init__(self):
        self.wiresharkAddr = ("127.0.0.1", 5555)
        self.wiresharkSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receiveCallback = lambda arr: arr

    @abstractmethod
    def _set_channel(self, channel):
        raise NotImplementedError()

    @abstractmethod
    def _send(self, data):
        raise NotImplementedError()

    @abstractmethod
    def _start(self):
        raise NotImplementedError()

    @abstractmethod
    def _close(self):
        raise NotImplementedError()

    def _get_CRC(self, package):
        packageBytes = bytes.fromhex(package)
        return hex(CRC16Kermit().calculate(packageBytes))[2:].zfill(4)

    def set_channel(self, channel):
        # TODO check channel is number and between 11 and 25
        self._set_channel(channel)

    def set_receive_callback(self, callback):
        self.receiveCallback = callback

    def start(self):
        self._start()

    def close(self):
        self._close()

    def receive(self, data):
        self.wiresharkSock.sendto(bytearray.fromhex(data + self._get_CRC(data)), self.wiresharkAddr)
        if self.receiveCallback:
            self.receiveCallback(data)

    def send(self, data):
        self.wiresharkSock.sendto(bytearray.fromhex(data + self._get_CRC(data)), self.wiresharkAddr)
        self._send(data)
