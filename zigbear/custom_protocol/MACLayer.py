class MACLayer:
    def __init__(self, phyConnector, network, address):
        self.network = network
        self.address = address
        self.connector = phyConnector
        self.sequence = 0

        self.connector.setReceiveCallback(self.receive)

    def newSequenceNumber(self):
        s = self.sequence
        self.sequence = (self.sequence + 1) % 256
        return s

    def send(self, data, destination):
        header = "6188"
        package = "{header}{seq:02x}{network:02x}{dest:02x}{src:02x}{data}".format(header = header, seq = self.newSequenceNumber(), network = self.network, dest = destination, src = self.address, data = data)
        print(package)
        self.connector.sendPacket(package)

    def receive(self, data):
        pass