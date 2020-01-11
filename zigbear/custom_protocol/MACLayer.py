from scapy.layers.dot15d4 import Dot15d4, Dot15d4Data


class MACLayer:
    def __init__(self, phyConnector, network, address):
        self.network = network
        self.address = address
        self.connector = phyConnector
        self.sequence = 0

        self.connector.set_receive_callback(self.receive)

    def new_sequence_number(self):
        s = self.sequence
        self.sequence = (self.sequence + 1) % 256
        return s

    def send(self, data, destination):
        ieee_fc = Dot15d4(fcf_reserved_1=0, fcf_panidcompress=1, fcf_ackreq=0,
                          fcf_pending=0, fcf_security=0, fcf_frametype=0x1,
                          fcf_srcaddrmode=0x2, fcf_framever=0x0, fcf_destaddrmode=0x2,
                          fcf_reserved_2=0x0, seqnum=self.new_sequence_number())

        ieee_data = Dot15d4Data(dest_panid=self.network, dest_addr=destination, src_addr=self.address)

        self.connector.send((ieee_fc / ieee_data / data).build().hex())

    def receive(self, data):
        ieee_fc = Dot15d4(data)

        ieee_data = Dot15d4Data(ieee_fc.payload)
