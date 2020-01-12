from scapy.packet import Raw

from zigbear.custom_protocol.stack import ProtocolStack


class Device:
    def __init__(self, connector):
        self.protocol_stack = ProtocolStack(connector)

    def send(self, destination, message):
        session = self.protocol_stack.connect(destination, 100)
        session.send(Raw(message))
        answer = session.receive().build()
        print("Answer: {}".format(answer))
        session.close()
