from zigbear.radio.connector import Connector

# based on https://github.com/g-oikonomou/sensniff/blob/master/sensniff.py

import serial
import struct

LINKTYPE_IEEE802_15_4_NOFCS = 230
LINKTYPE_IEEE802_15_4 = 195
MAGIC_NUMBER = 0xA1B2C3D4
VERSION_MAJOR = 2
VERSION_MINOR = 4
THISZONE = 0
SIGFIGS = 0
SNAPLEN = 0xFFFF
NETWORK = LINKTYPE_IEEE802_15_4

PCAP_GLOBAL_HDR_FMT = '<LHHlLLL'
PCAP_FRAME_HDR_FMT = '<LLLL'

SENSNIFF_MAGIC_LEGACY = bytearray((0x53, 0x6E, 0x69, 0x66))
SENSNIFF_MAGIC = bytearray((0xC1, 0x1F, 0xFE, 0x72))

pcap_global_hdr = bytearray(struct.pack(PCAP_GLOBAL_HDR_FMT, MAGIC_NUMBER,
                                        VERSION_MAJOR, VERSION_MINOR,
                                        THISZONE, SIGFIGS, SNAPLEN, NETWORK))

CMD_FRAME             = 0x00
CMD_CHANNEL           = 0x01
CMD_CHANNEL_MIN       = 0x02
CMD_CHANNEL_MAX       = 0x03
CMD_ERR_NOT_SUPPORTED = 0x7F
CMD_GET_CHANNEL       = 0x81
CMD_GET_CHANNEL_MIN   = 0x82
CMD_GET_CHANNEL_MAX   = 0x83
CMD_SET_CHANNEL       = 0x84
CMD_SEND_DATA         = 0x85
SNIFFER_PROTO_VERSION = 2

class CC2531Connector(Connector):
    def __write_command(self, cmd, len = 0, data = bytearray()):
        bytes = bytearray((SNIFFER_PROTO_VERSION, cmd))
        if len > 0:
            bytes += bytearray((len >> 8, len & 0xFF))
        if data is not None:
            bytes += data

        self.port.write(SENSNIFF_MAGIC)
        self.port.write(bytes)
        self.port.flush()

    def __read_frame(self):
        # Read the magic + 1 more byte
        b = self.port.read(5)
        size = len(b)

        if size == 0:
            return None
        if size < 5:
            #bytes but not part of a frame
            self.port.flushInput()
            return None

        if b[0:4] not in (SENSNIFF_MAGIC,SENSNIFF_MAGIC_LEGACY):
            # Peripheral UART output - print it
            per_out = self.port.readline().rstrip()
            return None

        # If we reach here:
        # Next byte == 1: Proto version 1, header follows
        # Next Byte != 1 && < 128. Old proto version. Frame follows, length == the byte
        b = bytearray(b)
        if b[4] != SNIFFER_PROTO_VERSION:
            # Legacy contiki sniffer support. Will slowly fade away
            size = b[4]
            b = self.port.read(size)
            
            if len(b) != size:
                # We got the magic right but subsequent bytes did not match
                # what we expected to receive
                self.port.flushInput()
                return None
            return b

        # If we reach here, we have a packet of proto ver SNIFFER_PROTO_VERSION
        # Read CMD and LEN
        b = self.port.read(3)
        size = len(b)

        if size < 3:
            #Read correct magic not followed by a frame header
            self.port.flushInput()
            return None

        b = bytearray(b)
        cmd = b[0]
        length = b[1] << 8 | b[2]

        if cmd == CMD_ERR_NOT_SUPPORTED:
            return None

        # Read the frame or command response
        b = self.port.read(length)
        if len(b) != length:
            # We got the magic right but subsequent bytes did not match
            # what we expected to receive
            self.port.flushInput()
            return None

        # If we reach here, b holds a frame or a command response of length len
        if cmd == CMD_FRAME:
            return b
        return None

        # If we reach here, we have a command response
        #b = bytearray(b)
        # We'll only ever see one of these if the user asked for it, so we are
        # running interactive. Print away
        #if cmd == CMD_CHANNEL:
        #    print('Sniffing in channel: %d' % (b[0],))
        #elif cmd == CMD_CHANNEL_MIN:
        #    print('Min channel: %d' % (b[0],))
        #elif cmd == CMD_CHANNEL_MAX:
        #    print('Max channel: %d' % (b[0],))
        #return None

    def __init__(self):
        super().__init__()
        self.port = '/dev/ttyACM0'
        self.baud = 460800
        self.timeout = 0.1
        self.port = serial.Serial(
            port = self.port,
            baudrate = self.baud,
            bytesize = serial.EIGHTBITS,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            xonxoff = False,
            rtscts = False,
            timeout = self.timeout)


    def _send(self, data):
        self.__write_command(CMD_SEND_DATA,len(bytearray.fromhex(data)), bytearray.fromhex(data))

    def _start(self):
        pass  # TODO

    def _close(self):
        pass  # TODO

    def _set_channel(self, channel):
        channel=int(channel)
        self.__write_command(CMD_SET_CHANNEL, 1, bytearray((channel,))) 
    
    def _receive(self):
        pass
