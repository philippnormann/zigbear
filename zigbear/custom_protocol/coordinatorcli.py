from cmd import Cmd

from zigbear.custom_protocol.Coordinator import Coordinator


class CoordinatorCli(Cmd):
    def __init__(self, connector):
        self.prompt = 'Zigbear/coordinator> '
        super().__init__()
        self.coordinator = Coordinator(connector)

    def do_devices(self, _):
        pass  # TODO print list of devices

    def do_info(self, _):
        self.coordinator.print_info()

    def do_start(self, _):
        self.coordinator.start_server()

    def do_stop(self, _):
        self.coordinator.stop_server()

    def do_toggle(self, arg: str):
        '''brightness <dest_addr>: toggle lamp'''
        try:
            dest_addr = int(arg)
            self.coordinator.toggle_lamp(dest_addr)
        except ValueError:
            print('invalid destination address')

    def do_brightness(self, arg: str):
        '''brightness <dest_addr> <brightness (0-255)>: set lamp to specific brightness'''
        args = arg.split()
        brightness = None
        dest_addr = None
        try:
            dest_addr = int(args[0])
        except:
            print('invalid destination address')
        try:
            brightness = int(args[1])
        except:
            print('invalid brightness value')
        if brightness is not None and dest_addr is not None:
            if 0 <= brightness <= 255:
                self.coordinator.set_lamp_brightness(dest_addr, brightness)
            else:
                print('brightness value must be between 0 and 255')

    def do_initiate(self, arg: str):
        try:
            dest_addr = int(arg)
            self.coordinator.initiate_contact(dest_addr)
        except ValueError:
            print('invalid destination address')

    def do_inits(self, _):
        self.coordinator.print_init()

    def do_sendkey(self, arg: str):
        try:
            dest_addr = int(arg)
            self.coordinator.pair_devices(dest_addr)
        except ValueError:
            print('invalid destination address')
