from nrf52840.Packetbuilder.nrfconnector import NrfConnector
from zigbear.custom_protocol import ApplicationLayer
from zigbear.custom_protocol import MACLayer
from zigbear.custom_protocol import NetworkLayer
from zigbear.custom_protocol import SecurityLayer


class Device:
    def __init__(self):
        self.connector = NrfConnector("/dev/ttyACM0")
        self.maclayer = MACLayer(self.connector, 0, 1)
        self.networklayer = NetworkLayer(self.maclayer)
        self.securitylayer = SecurityLayer(self.networklayer)
        self.application = ApplicationLayer(self.securitylayer)

    def send(self, destination, data):
        print("Sending: {}".format(data))



        self.networklayer.send(data, destination)
