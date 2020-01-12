import math

from scapy.packet import Raw

from zigbear.custom_protocol.protocol import NetworkHeader


class NetworkLayer:

    def __init__(self, MACLayer):
        self.MACLayer = MACLayer
        self.packet_id_cache = {}
        self.packet_receive_cache = {}

        self.receive_callback = lambda source, port, data: source
        self.MACLayer.set_receive_callback(self.receive)

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def get_packet_id(self, destination, port):
        if destination not in self.packet_id_cache:
            self.packet_id_cache[destination] = {}
        if port not in self.packet_id_cache[destination]:
            self.packet_id_cache[destination][port] = 0

        x = self.packet_id_cache[destination][port]
        self.packet_id_cache[destination][port] = (x + 1) % 256

        return x

    def send(self, destination, port, data):
        rawData = data.build()
        packetcount = math.ceil(len(rawData) / 100)

        packet_id = self.get_packet_id(destination, port)

        for i in range(packetcount):
            d = rawData[i*100:(i*100)+100]
            h = NetworkHeader(port = port, package_id = packet_id, sequence_number = i)
            h.frame_control.package_start = i == 0
            if i == 0:
                h.sequence_length = packetcount

            self.MACLayer.send(h / d, destination)

    # TODO Maybe seperated thread with queue for handling package, to avoid overflow of serial connection
    # TODO Maybe send ack package after receive package
    # TODO Maybe set timestamp of first package and clear cache after time
    def receive(self, source, data):
        h = NetworkHeader(data)
        if source not in self.packet_receive_cache:
            self.packet_receive_cache[source] = {}
        if h.port not in self.packet_receive_cache[source]:
            self.packet_receive_cache[source][h.port] = {}
        if h.package_id not in self.packet_receive_cache[source][h.port]:
            self.packet_receive_cache[source][h.port][h.package_id] = {}
            self.packet_receive_cache[source][h.port][h.package_id][-1] = {}

        self.packet_receive_cache[source][h.port][h.package_id][h.sequence_number] = h.payload
        if h.frame_control.package_start:
            self.packet_receive_cache[source][h.port][h.package_id][-1]['sequence_length'] = h.sequence_length

        if 'sequence_length' in self.packet_receive_cache[source][h.port][h.package_id][-1]:
            l = self.packet_receive_cache[source][h.port][h.package_id][-1]['sequence_length']
            if l + 1 == len(self.packet_receive_cache[source][h.port][h.package_id]):
                d = b""
                for i in range(l):
                    d = d + self.packet_receive_cache[source][h.port][h.package_id][i].build()
                self.packet_receive_cache[source][h.port].pop(h.package_id)
                self.receive_callback(source, h.port, Raw(d))
