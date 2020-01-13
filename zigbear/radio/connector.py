import socket
from abc import abstractmethod
from PyCRC.CRC16Kermit import CRC16Kermit


class Connector:
    def __init__(self, wireshark_host="127.0.0.1", wireshark_port=5555):
        self.wireshark_addr = (wireshark_host, wireshark_port)
        self.wireshark_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_callback = lambda arr: arr

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
        self.receive_callback = callback

    def start(self):
        self._start()

    def close(self):
        self._close()

    def receive(self, data):
        self.wireshark_sock.sendto(bytearray.fromhex(data + self._get_CRC(data)), self.wireshark_addr)
        if self.receive_callback:
            self.receive_callback(data)

    def send(self, data):
        self.wireshark_sock.sendto(bytearray.fromhex(data + self._get_CRC(data)), self.wireshark_addr)
        self._send(data)