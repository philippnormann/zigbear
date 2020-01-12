import time

from scapy.packet import Raw

from zigbear.custom_protocol.stack import ProtocolStack


class Coordinator:
    def __init__(self, connector):
        self.protocol_stack = ProtocolStack(connector)

    def start_server(self):
        def handler(session):
            data = session.receive()
            print(data)
            session.send(Raw("Length: {}".format(len(data))))
            session.close()

        listener = self.protocol_stack.listen(100, handler)
        time.sleep(100000)
        listener.close()
