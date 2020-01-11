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


class SecurityHeader(Packet):
    name = "Security Layer"
    fields_desc = [
        BitEnumField("key_id", 0, 2,
                     {0: 'no_key', 1: 'network_key', 2: 'private_key', 3: 'public_key'}),
        FlagsField("frame_control", 0, 6,
                   ['reserved0', 'reserved1', 'reserved2', 'reserved3', 'reserved4', 'reserved5']),
        ShortField("frame_checksum", 0)
    ]
