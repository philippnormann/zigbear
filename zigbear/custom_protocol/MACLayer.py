from scapy.layers.dot15d4 import Dot15d4, Dot15d4Data


class MACLayer:
    def __init__(self, connector, network, address):
        self.network = network
        self.address = address
        self.connector = connector
        self.sequence = 0

        self.receive_callback = lambda source, data: source
        self.connector.set_receive_callback(self.receive)

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def new_sequence_number(self):
        s = self.sequence
        self.sequence = (self.sequence + 1) % 256
        return s

    def send(self, data: bytes, destination: int):
        ieee_fc = Dot15d4(fcf_reserved_1=0, fcf_panidcompress=1, fcf_ackreq=0,
                          fcf_pending=0, fcf_security=0, fcf_frametype=0x1,
                          fcf_srcaddrmode=0x2, fcf_framever=0x0, fcf_destaddrmode=0x2,
                          fcf_reserved_2=0x0, seqnum=self.new_sequence_number())

        ieee_data = Dot15d4Data(dest_panid=self.network, dest_addr=destination, src_addr=self.address)

        self.connector.send((ieee_fc / ieee_data / data).build())

    def receive(self, data: bytes):
        try:
            ieee_fc = Dot15d4(data)
            ieee_data = ieee_fc.payload
        except:
            return  # TODO log error in debug level

        if (ieee_data.dest_panid == self.network or ieee_data.dest_panid == 0xffff) \
                and (ieee_data.dest_addr == self.address or ieee_data.dest_addr == 0xffff):
            self.receive_callback(ieee_data.src_addr, ieee_data.payload)
