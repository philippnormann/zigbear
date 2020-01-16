import math
import threading
import time
from datetime import datetime, timedelta

from scapy.packet import Raw

from zigbear.custom_protocol.protocol import NetworkHeader

MAX_PACKAGE_LENGTH = 80


class NetworkLayer:

    def __init__(self, MACLayer):
        self.MACLayer = MACLayer
        self.packet_id_cache = {}
        self.packet_receive_cache = {}
        self.packet_send_cache = {}

        self.receive_callback = lambda source, port, data: source
        self.MACLayer.set_receive_callback(self.receive)

        self.thread = threading.Thread(target=self.run_retry, args=(), daemon=True)
        self.thread.start()

    def run_retry(self):
        while True:
            for destination in list(self.packet_send_cache):
                for port in list(self.packet_send_cache[destination]):
                    for packet_id in list(self.packet_send_cache[destination][port]):
                        for sequence_number in list(self.packet_send_cache[destination][port][packet_id]):
                            p = self.packet_send_cache[destination][port][packet_id][sequence_number]
                            if datetime.now() - p['time'] > timedelta(seconds=math.pow(p['retry'], 2)):
                                self.MACLayer.send(p['packet'], destination)
                                p['retry'] = p['retry'] + 1
                                p['time'] = datetime.now()
                                if p['retry'] >= 3:
                                    self.abort_retries(destination, port, packet_id, sequence_number)
            time.sleep(1)

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

    def send(self, destination, port, data, ack_req=True):
        rawData = data.build()
        packetcount = math.ceil(len(rawData) / MAX_PACKAGE_LENGTH)

        packet_id = self.get_packet_id(destination, port)

        for i in range(packetcount):
            d = rawData[i * MAX_PACKAGE_LENGTH:(i * MAX_PACKAGE_LENGTH) + MAX_PACKAGE_LENGTH]
            h = NetworkHeader(port=port, package_id=packet_id, sequence_number=i)
            h.frame_control.package_start = i == 0
            h.frame_control.ack_req = ack_req
            if i == 0:
                h.sequence_length = packetcount

            p = h / d

            self.MACLayer.send(p, destination)

            if ack_req:
                if destination not in self.packet_send_cache:
                    self.packet_send_cache[destination] = {}
                if port not in self.packet_send_cache[destination]:
                    self.packet_send_cache[destination][port] = {}
                if packet_id not in self.packet_send_cache[destination][port]:
                    self.packet_send_cache[destination][port][packet_id] = {}
                if i not in self.packet_send_cache[destination][port][packet_id]:
                    self.packet_send_cache[destination][port][packet_id][i] = {'time': datetime.now(), 'packet': p, 'retry': 0}

    def send_ack(self, source, port, package_id, sequence_number):
        h = NetworkHeader(port=port, package_id=package_id, sequence_number=sequence_number)
        h.frame_control.ack = True

        self.MACLayer.send(h, source)

    def abort_retries(self, destination, port, package_id, sequence_number):
        if destination in self.packet_send_cache \
                and port in self.packet_send_cache[destination] \
                and package_id in self.packet_send_cache[destination][port] \
                and sequence_number in self.packet_send_cache[destination][port][package_id]:
            self.packet_send_cache[destination][port][package_id].pop(sequence_number)
            if not self.packet_send_cache[destination][port][package_id]:
                self.packet_send_cache[destination][port].pop(package_id)
                if not self.packet_send_cache[destination][port]:
                    self.packet_send_cache[destination].pop(port)
                    if not self.packet_send_cache[destination]:
                        self.packet_send_cache.pop(destination)

    # TODO Maybe seperated thread with queue for handling package, to avoid overflow of serial connection
    # TODO Maybe send ack package after receive package
    # TODO Maybe set timestamp of first package and clear cache after time
    def receive(self, source, data):
        h = NetworkHeader(data)
        if h.frame_control.ack:
            self.abort_retries(source, h.port, h.package_id, h.sequence_number)
        else:
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

            if h.frame_control.ack_req:
                self.send_ack(source, h.port, h.package_id, h.sequece_number)

            if 'sequence_length' in self.packet_receive_cache[source][h.port][h.package_id][-1]:
                l = self.packet_receive_cache[source][h.port][h.package_id][-1]['sequence_length']
                if l + 1 == len(self.packet_receive_cache[source][h.port][h.package_id]):
                    d = b""
                    for i in range(l):
                        d = d + self.packet_receive_cache[source][h.port][h.package_id][i].build()
                    self.packet_receive_cache[source][h.port].pop(h.package_id)
                    self.receive_callback(source, h.port, Raw(d))
