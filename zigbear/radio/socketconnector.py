import socket
import threading
from zigbear.radio.connector import Connector

class SocketConnector(Connector):
    def __init__(self, receive_port, target_port):
        super().__init__()
        self.target_port = int(target_port)
        self.receive_port = int(receive_port)
        self.send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send(self, data: bytes):
        self.send_socket.sendto(data,("127.0.0.1", self.target_port))

    def read_from_socket(self):
        listening_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        listening_socket.bind(("127.0.0.1", self.receive_port))
        t = threading.currentThread()
        while getattr(t, "continue_sniffing", True):
            data, addr = listening_socket.recvfrom(4096)
            self.receive(data)

    def _start(self):
        if (not hasattr(self, 'thread')) or (not self.thread.isAlive()):
            self.thread = threading.Thread(target=self.read_from_socket, args=(), daemon=True)
            self.thread.start()
        else:
            print("Sniffer is already running")

    def _close(self):
        self.thread.continue_sniffing = False
        self.thread.join()

    def _set_channel(self, channel):
        print("set channel: {}".format(channel))