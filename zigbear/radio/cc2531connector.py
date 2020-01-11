from zigbear.radio.connector import Connector

# based on https://github.com/g-oikonomou/sensniff/blob/master/sensniff.py

import serial
import struct
import threading
import logging
import logging.handlers
import sys

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

CMD_FRAME = 0x00
CMD_CHANNEL = 0x01
CMD_ERR_NOT_SUPPORTED = 0x7F
CMD_SET_CHANNEL = 0x84
CMD_SEND_DATA = 0x85
SNIFFER_PROTO_VERSION = 2

logger = logging.getLogger(__name__)


class CC2531Connector(Connector):

    def __init__(self):
        super().__init__()
        self.started = False
        self.port = '/dev/ttyACM0'
        self.baud = 460800
        self.timeout = 0.1
        self.__sensniff_magic_legacy = bytearray((0x53, 0x6E, 0x69, 0x66))
        self.__sensniff_magic = bytearray((0xC1, 0x1F, 0xFE, 0x72))
        try:
            self.port = serial.Serial(
                port=self.port,
                baudrate=self.baud,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                xonxoff=False,
                rtscts=False,
                timeout=self.timeout)
            self.port.flushInput()
            self.port.flushOutput()
        except (serial.SerialException, ValueError, IOError, OSError) as e:
            logger.error('Error opening port: %s' % (self.port,))
            logger.error('The error was: %s' % (e.args,))
            sys.exit(1)
        logger.info('Serial port %s opened' % (self.port.name))

    def _send(self, data):
        self.__write_command(CMD_SEND_DATA, len(bytearray.fromhex(data)), bytearray.fromhex(data))

    def _start(self):
        if (not self.started) or (not self.thread.isAlive()):
            self.started = True
            self.thread = threading.Thread(target=self.__listen, args=(), daemon=True)
            self.thread.start()
        else:
            print("Sniffer is already running")

    def _close(self):
        self.started = False

    def _set_channel(self, channel):
        channel = int(channel)
        self.__write_command(CMD_SET_CHANNEL, 1, bytearray((channel,)))

    def __listen(self):
        while self.started:
            data = self.__read_frame().hex()
            if (len(data) > 0):
                logger.info(data)
                self.receive(data)

    def __write_command(self, cmd, len=0, data=bytearray()):
        bytes = bytearray((SNIFFER_PROTO_VERSION, cmd))
        if len > 0:
            bytes += bytearray((len >> 8, len & 0xFF))
        if data is not None:
            bytes += data

        self.port.write(SENSNIFF_MAGIC)
        self.port.write(bytes)
        self.port.flush()

    def __read_frame(self):
        try:
            # Read the magic + 1 more byte
            b = self.port.read(5)
            size = len(b)
        except (IOError, OSError) as e:
            logger.error('Error reading port: %s' % (self.port.port,))
            logger.error('The error was: %s' % (e.args,))
            sys.exit(1)

        if size == 0:
            return b
        if size < 5:
            logger.warning('Read %d bytes but not part of a frame'
                           % (size,))
            self.port.flushInput()
            return ''
        if b[0:4] not in (self.__sensniff_magic, self.__sensniff_magic_legacy):
            # Peripheral UART output - print it
            per_out = self.port.readline().rstrip()
            try:
                logger.info("Peripheral: %s%s" % (b.decode(), per_out.decode()))
            except UnicodeDecodeError as e:
                logger.info("Error decoding peripheral output: %s" % e)
            return ''

        # If we reach here:
        # Next byte == 1: Proto version 1, header follows
        # Next Byte != 1 && < 128. Old proto version. Frame follows, length == the byte
        b = bytearray(b)
        if b[4] != SNIFFER_PROTO_VERSION:
            # Legacy contiki sniffer support. Will slowly fade away
            size = b[4]
            try:
                b = self.port.read(size)
            except (IOError, OSError) as e:
                logger.error('Error reading port: %s' % (self.port.port,))
                logger.error('The error was: %s' % (e.args,))
                sys.exit(1)

            if len(b) != size:
                # We got the magic right but subsequent bytes did not match
                # what we expected to receive
                logger.warning('Read correct magic not followed by a frame')
                logger.warning('Expected %d bytes, got %d' % (size, len(b)))
                self.port.flushInput()
                return ''

            logger.info('Read a frame of size %d' % (len(b),))
            return b

        # If we reach here, we have a packet of proto ver SNIFFER_PROTO_VERSION
        # Read CMD and LEN
        try:
            size = 0
            b = self.port.read(3)
            size = len(b)

        except (IOError, OSError) as e:
            logger.error('Error reading port: %s' % (self.port.port,))
            logger.error('The error was: %s' % (e.args[0],))
            sys.exit(1)

        if size < 3:
            logger.warning('Read correct magic not followed by a frame header')
            logger.warning('Expected 3 bytes, got %d' % (len(b),))
            self.port.flushInput()
            return ''

        b = bytearray(b)
        cmd = b[0]
        length = b[1] << 8 | b[2]

        if cmd == CMD_ERR_NOT_SUPPORTED:
            logger.warning("Peripheral reports unsupported command")
            return ''

        # Read the frame or command response
        b = self.port.read(length)
        if len(b) != length:
            # We got the magic right but subsequent bytes did not match
            # what we expected to receive
            logger.warning('Read correct header not followed by a frame')
            logger.warning('Expected %d bytes, got %d' % (length, len(b)))
            self.port.flushInput()
            return ''

        # If we reach here, b holds a frame or a command response of length len
        if cmd == CMD_FRAME:
            logger.info('Read a frame of size %d' % (length,))
            return b
