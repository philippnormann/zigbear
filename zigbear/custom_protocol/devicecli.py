from cmd import Cmd

from zigbear.custom_protocol.Device import Device


class DeviceCli(Cmd):
    def __init__(self, connector):
        super().__init__()
        self.prompt = 'Zigbear/device> '
        self.device = Device(connector)

    def do_test(self, arg):
        self.device.send(0xffff, "Hallo, dies ist eine kleine Nachricht zum Testes, ob das Spltten von Paketen richtig funktioniert. Deshalb muss diese Nachrichte eine gewisse länge haben.")
