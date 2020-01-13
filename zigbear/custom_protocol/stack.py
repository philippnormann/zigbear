from scapy.packet import Raw

from zigbear.custom_protocol.ApplicationLayer import ApplicationLayer
from zigbear.custom_protocol.MACLayer import MACLayer
from zigbear.custom_protocol.NetworkLayer import NetworkLayer


class ProtocolStack:
    def __init__(self, connector):
        self.connector = connector
        self.maclayer = MACLayer(self.connector, 0, 0)
        self.networklayer = NetworkLayer(self.maclayer)
        # self.securitylayer = SecurityLayer(self.networklayer)
        self.application = ApplicationLayer(self.networklayer)

    def set_panid(self, pan):
        self.maclayer.network = pan

    def get_panid(self):
        return self.maclayer.network

    def set_address(self, address):
        self.maclayer.address = address

    def get_address(self):
        return self.maclayer.address

    def get_networkkey(self):
        return ""  # TODO

    def get_privatekey(self):
        return ""  # TODO

    def get_publickey(self):
        return ""  # TODO

    def get_session_count(self):
        count = 0
        for s in self.application.sessions:
            count += len(self.application.sessions[s])
        return count

    def get_listeners_count(self):
        return len(self.application.listeners)

    def connect(self, destination, port):
        return self.application.connect(destination, port)

    def listen(self, port, handler):
        return self.application.listen(port, handler)

    def status(self):
        return {
                    "panid": self.get_panid(),
                    "address": self.get_address(),
                    "networkkey": self.get_networkkey(),
                    "privatekey": self.get_privatekey(),
                    "publickey": self.get_publickey(),
                    "session_count": self.get_session_count(),
                    "listeners_count": self.get_listeners_count()
                }
