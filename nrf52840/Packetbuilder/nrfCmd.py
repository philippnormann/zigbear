import sys, getopt
from cmd import Cmd
from Packetbuilder.nrfconnector import *
from Packetbuilder.packetbuilder import *

class nrfCmd(Cmd):
    def __init__(self, comPort, channel):
        Cmd.__init__(self)
        self.prompt = 'nrfCmd> '
        self.intro = "Welcome! Type ? to list commands"
        self.nrfConnector = NrfConnector(comPort)
        if not channel:
            channel = 11
        self.do_channel(channel)
    
    def do_comport(self, _):
        '''comport: shows comport'''
        print(self.comPort)
    
    def do_channel(self, inp):
        '''channel: shows channel\nchannel <channel>: sets channel'''
        if inp:
            self.nrfConnector.setChannel(inp)
        else:
            self.nrfConnector.getChannel()
    
    def do_start(self, _):
        '''start: starts the barrage of packets (!currently no way to stop!)'''
        self.nrfConnector.start()
    
    def do_send(self, inp):
        '''send <hexStr>: send the hexStr'''
        self.nrfConnector.sendPacket(inp)
            
    def do_sendexample(self, inp):
        '''sendexample <frameCounter> <on/off>: sends example packet with frameCounter'''
        frameCounter, onoff = inp.split()
        hexString = create_example_frame(int(frameCounter), onoff == "on")
        self.nrfConnector.sendPacket(hexString.build().hex())
    
    def do_exit(self, inp):
        '''exits the CMD'''
        print("Buh-Bye")
        return True


if __name__ == '__main__':
    helpText = 'nrfconnector.py (-p <ComPort> | --port <ComPort>) [(-c <ZigBeeChannel> | --port <ZigBeeChannel>) -h]'
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:hp:", ["channel=", "port="])
    except getopt.GetoptError as err:
        print(helpText)
        print(str(err))
        sys.exit(2)
    comPort = None
    channel = None
    for opt, arg in opts:
        if opt == '--channel':
            channel = int(arg)
        elif opt == '--port':
            comPort = arg
        elif opt == '-c':
            channel = int(arg)
        elif opt == '-p':
            comPort = arg
        elif opt == '-h':
            print(helpText)
            sys.exit()
        else:
            assert False, "unhandled option"
    if not (comPort):
        print(helpText)
        sys.exit(2)
    nrfC = nrfCmd(comPort, channel)
    nrfC.cmdloop()