from scapy.fields import ByteField, ShortField, SignedShortField, FlagsField, BitEnumField, ConditionalField, \
    SignedIntField, SignedByteField
from scapy.packet import Packet


class NetworkHeader(Packet):
    name = "Network Layer"
    fields_desc = [
        FlagsField("frame_control", 48, 8,
                   ['reserved0', 'reserved1', 'reserved2', 'reserved3', 'reserved4', 'package_start', 'ack_req', 'ack']),
        ByteField("port", 0),
        ByteField("package_id", 0),
        ConditionalField(
            ShortField("sequence_length", 0),
            lambda pkt: pkt.frame_control.package_start
        ),
        ShortField("sequence_number", 0)
    ]
