import sys, getopt
from cmd import Cmd
from zigbear.zigbee.packetbuilder import *


class ZigbeeCli(Cmd):
    def __init__(self, connector):
        Cmd.__init__(self)
        self.prompt = 'Zigbear/zigbee> '
        self.connector = connector
            
    def do_sendexample(self, inp):
        '''sendexample <frameCounter> <on/off>: sends example packet with frameCounter'''
        frameCounter, onoff = inp.split()
        hexString = create_example_frame(int(frameCounter), onoff == "on")
        self.connector.send(hexString.build().hex())
    
    def do_exit(self, inp):
        '''exits the CMD'''
        return True
