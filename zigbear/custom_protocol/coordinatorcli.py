from cmd import Cmd

from zigbear.custom_protocol.Coordinator import Coordinator


class CoordinatorCli(Cmd):
    def __init__(self, connector):
        self.prompt = 'Zigbear/coordinator> '
        super().__init__()
        self.coordinator = Coordinator(connector)

    def do_devices(self, _):
        pass # TODO print list of devices

    def do_info(self, _):
        pass # TODO print info like keys, ...

    def do_accept(self, arg):
        self.coordinator.start_server()
        pass # TODO accept a new device with name and public key

