from scapy.packet import Raw

from zigbear.custom_protocol.ApplicationLayer import ApplicationLayer
from zigbear.custom_protocol.MACLayer import MACLayer
from zigbear.custom_protocol.NetworkLayer import NetworkLayer


class ProtocolStack:
    def __init__(self, connector):
        self.connector = connector
        self.maclayer = MACLayer(self.connector, 0, 1)
        self.networklayer = NetworkLayer(self.maclayer)
        #self.securitylayer = SecurityLayer(self.networklayer)
        self.application = ApplicationLayer(self.networklayer)

    def set_panid(self, pan):
        self.maclayer.network = pan

    def get_panid(self):
        return self.maclayer.network

    def set_address(self, address):
        self.maclayer.address = address

    def get_address(self):
        return self.maclayer.address

    def connect(self, destination, port):
        return self.application.connect(destination, port)

    def listen(self, port, handler):
        return self.application.listen(port, handler)
