from cmd import Cmd


class CoordinatorCli(Cmd):
    def __init__(self, connector):
        super().__init__()

    def do_devices(self, _):
        pass # TODO print list of devices

    def do_info(self, _):
        pass # TODO print info like keys, ...

    def do_accept(self, arg):
        pass # TODO accept a new device with name and public key

