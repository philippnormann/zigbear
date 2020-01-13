from cmd import Cmd

from zigbear.custom_protocol.Device import Device


class DeviceCli(Cmd):
    def __init__(self, connector):
        super().__init__()
        self.prompt = 'Zigbear/device> '
        self.device = Device(connector)

    def do_send(self, arg):
        self.device.send(1, arg)

    def do_info(self, arg):
        self.device.print_info()
