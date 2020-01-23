import time

from scapy.packet import Raw

from zigbear.custom_protocol.scapy_layers import ZigbearLightControlLayer
from zigbear.custom_protocol.stack import ProtocolStack


class Coordinator:
    def __init__(self, connector):
        self.protocol_stack = ProtocolStack(connector, b"network_keynetwork_keynetwork_ke")
        self.protocol_stack.set_address(1)
        self.server = None

    def start_server(self):
        if self.server is not None:
            print("Server already running.")
        else:
            def handler(session):
                data = session.receive()
                print("Message from {} with data {}".format(session.other, data))
                session.send(Raw("Length: {}".format(len(data))))
                session.close()

            self.server = self.protocol_stack.listen(100, handler)

    def stop_server(self):
        if self.server is None:
            print("Currenty no server is running")
        else:
            self.server.close()
            self.server = None


    def toggle_lamp(self, destination: int):
        session = self.protocol_stack.connect(destination, 100)
        session.send(ZigbearLightControlLayer(message_type=0))
        session.close()

    def set_lamp_brightness(self, destination: int, brightness: int):
        session = self.protocol_stack.connect(destination, 100)
        session.send(ZigbearLightControlLayer(message_type=1, brightness=brightness))
        session.close()

    def initiate_contact(self, destination: int):
        session = self.protocol_stack.connect(destination, 100)
        session.send_initiation_packet()
        session.close()

    def pair_devices(self, destination: int):
        session = self.protocol_stack.connect(destination, 100)
        session.send_network_key()
        session.close()

    def start(self):
        pass  # TODO

    def close(self):
        pass  # TODO

    def set_panid(self, panid):
        self.protocol_stack.set_panid(panid)

    def set_address(self, address):
        self.protocol_stack.set_address(address)

    def set_network_key(self, networkkey):
        self.protocol_stack.set_network_key(networkkey)

    def list_devices(self):
        pass  # TODO

    def print_init(self):
        print("""
INIT DEVICES: {init_devices}
                """.format(**self.protocol_stack.get_init_devices()).strip())

    def print_info(self):
        print("""
PAN ID: {panid}
Address: {address}
Count Session: {session_count}
Count Listeners: {listeners_count}
Network key: {networkkey}
                """.format(**self.protocol_stack.status()).strip())
