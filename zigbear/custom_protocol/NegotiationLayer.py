from scapy.packet import Packet
from scapy.fields import StrField, BitEnumField, FlagsField, XLEIntField, ConditionalField, BitField

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