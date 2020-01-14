import socket
from struct import pack
from abc import abstractmethod


class Connector:
    def __init__(self, wireshark_host="127.0.0.1", wireshark_port=5555):
        self.wireshark_addr = (wireshark_host, wireshark_port)
        self.wireshark_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.receive_callback = lambda arr: arr

    @abstractmethod
    def _set_channel(self, channel: int):
        raise NotImplementedError()

    @abstractmethod
    def _send(self, data: bytes):
        raise NotImplementedError()

    @abstractmethod
    def _start(self):
        raise NotImplementedError()

    @abstractmethod
    def _close(self):
        raise NotImplementedError()

    def _get_CRC(self, data: bytes) -> bytes:
        crc = 0
        for i in range(0, len(data)):
            c = data[i]
            q = (crc ^ c) & 15  # Do low-order 4 bits
            crc = (crc // 16) ^ (q * 4225)
            q = (crc ^ (c // 16)) & 15  # And high 4 bits
            crc = (crc // 16) ^ (q * 4225)
        return pack('<H', crc)  # return as bytes in little endian order

    def set_channel(self, channel: int):
        if 11 <= channel <= 25:
            self._set_channel(channel)

    def set_receive_callback(self, callback: object):
        if callable(callback):
            self.receive_callback = callback

    def start(self):
        self._start()

    def close(self):
        self._close()

    def receive(self, data: bytes):
        self.wireshark_sock.sendto(
            data + self._get_CRC(data), self.wireshark_addr)
        if self.receive_callback:
            self.receive_callback(data)

    def send(self, data: bytes):
        self.wireshark_sock.sendto(
            data + self._get_CRC(data), self.wireshark_addr)
        self._send(data)
