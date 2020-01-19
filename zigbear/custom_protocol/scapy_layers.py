from scapy.fields import ByteField, ShortField, SignedShortField, FlagsField, BitEnumField, ConditionalField, \
    SignedIntField, SignedByteField, StrField, XLEIntField, BitField
from scapy.packet import Packet

class NetworkHeader(Packet):
    name = "Network Layer"
    fields_desc = [
        FlagsField("frame_control", 0, 8,
                   ['reserved0', 'reserved1', 'reserved2', 'reserved3', 'reserved4', 'package_start', 'ack_req', 'ack']),
        ByteField("port", 0),
        ByteField("package_id", 0),
        ConditionalField(
            ShortField("sequence_length", 0),
            lambda pkt: pkt.frame_control.package_start
        ),
        ShortField("sequence_number", 0)
    ]

class ZigbearSecurityLayer(Packet):
    name = "Zigbear Security Header"
    fields_desc = [
        # Message Info (1 octet)
        # Informational flags
        FlagsField("flags", 0, 6, ['public_key_request', 'reserved1','reserved2','reserved3','reserved4','reserved5']),
        # Message type
        BitEnumField("message_type", 0, 2, {
            0: 'no_encryption',
            1: 'public_key_transmission',
            2: 'network_key_transmission',
            3: 'symencrypted_data',
        }),
        # Frame counter (4 octets)
        XLEIntField("fc", 0),  # provide frame freshness and prevent duplicate frames
        # Payload
        # Message Authentication Code (16 Byte CMAC for example)
        # For transmission of network key: Other key derived from shared key
        # Otherwise: tbd
        ConditionalField(BitField("mac", 0, 128), lambda pkt: pkt.getfieldval("message_type") > 1),
        # Can be 80 Bytes DER serialized ECDH public key from SECP224R1
        # Can be the transmitted network key encrypted with a key derived from the shared key
        # Can be data encrpted with the network key
        StrField("data", "")
    ]

class ZigbearLightControlLayer(Packet):
    name = "Zigbear Light Control Layer"
    fields_desc = [
        # Informational flags
        FlagsField("flags", 0, 6, ['reserved0', 'reserved1','reserved2','reserved3','reserved4','reserved5']),
        # Message type
        BitEnumField("message_type", 0, 2, {
            0: 'toggle',
            1: 'set_brightness'
        }),
        ConditionalField(ByteField("brightness", 0), lambda pkt: pkt.getfieldval("message_type") == 1)
    ]