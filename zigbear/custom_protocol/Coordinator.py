from zigbear.custom_protocol.ApplicationLayer import ApplicationLayer
from zigbear.custom_protocol.MACLayer import MACLayer
from zigbear.custom_protocol.NetworkLayer import NetworkLayer
from zigbear.custom_protocol.SecurityLayer import SecurityLayer


class Coordinator:
    def __init__(self, connector):
        self.connector = connector
        self.maclayer = MACLayer(self.connector, 0, 1)
        self.networklayer = NetworkLayer(self.maclayer)
        self.securitylayer = SecurityLayer(self.networklayer)
        self.application = ApplicationLayer(self.securitylayer)

    def send(self, destination, data):
        print("Sending: {}".format(data))



        self.networklayer.send(data, destination)
