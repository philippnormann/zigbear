from cmd import Cmd

from zigbear.custom_protocol.coordinatorcli import CoordinatorCli
from zigbear.custom_protocol.devicecli import DeviceCli
from zigbear.radio.cc2531connector import CC2531Connector
from zigbear.radio.mockconnector import MockConnector
from zigbear.radio.nrfconnector import NrfConnector
from zigbear.radio.raspbeeconnector import RaspbeeConnector
from zigbear.zigbee.zigbeeCli import ZigbeeCli


class ZigbearCli(Cmd):
    def __init__(self):
        super().__init__()
        self.connector = None
        self.prompt = "zigbear> "
        self.intro = "Welcome! Type ? to list commands"

    def do_channel(self, arg):
        '''channel <channel>: set the channel in the current connector'''
        if len(arg) == 0:
            print()
        else:
            self.connector.set_channel(arg)

    def do_zigbee(self, arg):
        if self.connector:
            ZigbeeCli(self.connector).cmdloop()
        else:
            print("please specify a radio connector")

    def do_device(self, arg):
        if self.connector:
            DeviceCli(self.connector).cmdloop()
        else:
            print("please specify a radio connector")

    def do_coordinator(self, arg):
        if self.connector:
            CoordinatorCli(self.connector).cmdloop()
        else:
            print("please specify a radio connector")

    def do_start(self, _):
        '''start: starts sending packets to udp port 5555'''
        self.connector.start()

    def do_stop(self, _):
        '''stop: stops sending packets to udp port 5555'''
        self.connector.close()

    def do_send(self, inp):
        '''send <hexStr>: send the hexStr'''
        self.connector.send(inp)

    def do_connector(self, arg):
        '''connector <type>: sets the connector for radio'''
        if arg == "nrf":
            port = input("COM port: ")
            self.connector = NrfConnector(port)
        elif arg == "cc2531":
            self.connector = CC2531Connector()
        elif arg == "raspbee":
            self.connector = RaspbeeConnector()
        elif arg == "mock":
            self.connector = MockConnector()
        else:
            self.connector = None

    def do_exit(self, inp):
        '''exits the CMD'''
        print("Bye")
        return True
