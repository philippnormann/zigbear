from random import random

from scapy.packet import Raw

from zigbear.custom_protocol.stack import ProtocolStack
from zigbear.custom_protocol.virtual_lamp import Lamp


class Device:
    @staticmethod
    def random_id():
        return int(random() * 0xFFFD) + 1

    def __init__(self, connector):
        self.protocol_stack = ProtocolStack(connector)
        self.protocol_stack.set_address(Device.random_id())

    def send(self, destination, message):
        session = self.protocol_stack.connect(destination, 100)
        session.send(Raw(message))
        answer = session.receive()
        print("Answer: {}".format(answer))
        session.close()

    def start_lamp(self):
        lamp = Lamp(self.protocol_stack)
        lamp.wait_for_input()

    def print_info(self):
        print("""
PAN ID: {panid}
Address: {address}
Count Session: {session_count}
Count Listeners: {listeners_count}
Network key: {networkkey}
Private key: {privatekey}
Public key: {publickey}
                """.format(**self.protocol_stack.status()).strip())

    def find_network(self):
        pass  # TODO

    def join_network(self, panid):
        pass  # TODO

    def start(self):
        pass  # TODO

    def close(self):
        pass  # TODO
