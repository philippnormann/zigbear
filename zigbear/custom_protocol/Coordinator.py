import time

from scapy.packet import Raw

from zigbear.custom_protocol.stack import ProtocolStack


class Coordinator:
    def __init__(self, connector):
        self.protocol_stack = ProtocolStack(connector)
        self.protocol_stack.set_address(1)

    def start_server(self):
        def handler(session):
            data = session.receive()
            print("Message from {} with data {}".format(session.other, data))
            session.send(Raw("Length: {}".format(len(data))))
            session.close()

        listener = self.protocol_stack.listen(100, handler)
        time.sleep(100000)
        listener.close()

    def start(self):
        pass  # TODO

    def close(self):
        pass  # TODO

    def set_panid(self, panid):
        self.protocol_stack.set_panid(panid)

    def set_address(self, address):
        self.protocol_stack.set_address(address)

    def set_network_key(self, networkkey):
        pass  # TODO

    def list_devices(self):
        pass  # TODO

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
