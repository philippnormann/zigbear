from scapy.layers.zigbee import *

from scapy.packet import Packet
from scapy.fields import ByteField, ConditionalField, StrField, \
    ByteEnumField, EnumField, BitEnumField, FlagsField, IntField
from scapy.layers.dot15d4 import dot15d4AddressField
from scapy.fields import ByteField, ConditionalField, StrField, \
    ByteEnumField, EnumField, BitEnumField, FlagsField, IntField
from scapy.layers.dot15d4 import dot15d4AddressField
from scapy.layers.zigbee import *
from scapy.packet import Packet

# ZigBee Cluster Library Identifiers, Table 2.2 ZCL
_zcl_cluster_identifier = {
    # Functional Domain: General
    0x0000: "basic",
    0x0001: "power_configuration",
    0x0002: "device_temperature_configuration",
    0x0003: "identify",
    0x0004: "groups",
    0x0005: "scenes",
    0x0006: "on_off",
    0x0007: "on_off_switch_configuration",
    0x0008: "level_control",
    0x0009: "alarms",
    0x000a: "time",
    0x000b: "rssi_location",
    0x000c: "analog_input",
    0x000d: "analog_output",
    0x000e: "analog_value",
    0x000f: "binary_input",
    0x0010: "binary_output",
    0x0011: "binary_value",
    0x0012: "multistate_input",
    0x0013: "multistate_output",
    0x0014: "multistate_value",
    0x0015: "commissioning",
    # 0x0016 - 0x00ff reserved
    # Functional Domain: Closures
    0x0100: "shade_configuration",
    # 0x0101 - 0x01ff reserved
    # Functional Domain: HVAC
    0x0200: "pump_configuration_and_control",
    0x0201: "thermostat",
    0x0202: "fan_control",
    0x0203: "dehumidification_control",
    0x0204: "thermostat_user_interface_configuration",
    # 0x0205 - 0x02ff reserved
    # Functional Domain: Lighting
    0x0300: "color_control",
    0x0301: "ballast_configuration",
    # Functional Domain: Measurement and sensing
    0x0400: "illuminance_measurement",
    0x0401: "illuminance_level_sensing",
    0x0402: "temperature_measurement",
    0x0403: "pressure_measurement",
    0x0404: "flow_measurement",
    0x0405: "relative_humidity_measurement",
    0x0406: "occupancy_sensing",
    # Functional Domain: Security and safethy
    0x0500: "ias_zone",
    0x0501: "ias_ace",
    0x0502: "ias_wd",
    # Functional Domain: Protocol Interfaces
    0x0600: "generic_tunnel",
    0x0601: "bacnet_protocol_tunnel",
    0x0602: "analog_input_regular",
    0x0603: "analog_input_extended",
    0x0604: "analog_output_regular",
    0x0605: "analog_output_extended",
    0x0606: "analog_value_regular",
    0x0607: "analog_value_extended",
    0x0608: "binary_input_regular",
    0x0609: "binary_input_extended",
    0x060a: "binary_output_regular",
    0x060b: "binary_output_extended",
    0x060c: "binary_value_regular",
    0x060d: "binary_value_extended",
    0x060e: "multistate_input_regular",
    0x060f: "multistate_input_extended",
    0x0610: "multistate_output_regular",
    0x0611: "multistate_output_extended",
    0x0612: "multistate_value_regular",
    0x0613: "multistate_value",
    # Smart Energy Profile Clusters
    0x0700: "price",
    0x0701: "demand_response_and_load_control",
    0x0702: "metering",
    0x0703: "messaging",
    0x0704: "smart_energy_tunneling",
    0x0705: "prepayment",
    # Functional Domain: General
    # Key Establishment
    0x0800: "key_establishment",
}

# ZigBee stack profiles
_zcl_profile_identifier = {
    0x0000: "ZigBee_Stack_Profile_1",
    0x0101: "IPM_Industrial_Plant_Monitoring",
    0x0104: "HA_Home_Automation",
    0x0105: "CBA_Commercial_Building_Automation",
    0x0107: "TA_Telecom_Applications",
    0x0108: "HC_Health_Care",
    0x0109: "SE_Smart_Energy_Profile",
}


class ZigbeeAppDataPayload2(Packet):
    name = "Zigbee Application Layer Data Payload (General APS Frame Format)"
    fields_desc = [
        # Frame control (1 octet)
        FlagsField("frame_control", 2, 4,
                   ['reserved1', 'security', 'ack_req', 'extended_hdr']),
        BitEnumField("delivery_mode", 0, 2,
                     {0: 'unicast', 1: 'indirect',
                      2: 'broadcast', 3: 'group_addressing'}),
        BitEnumField("aps_frametype", 0, 2,
                     {0: 'data', 1: 'command', 2: 'ack'}),
        # Destination endpoint (0/1 octet)
        ConditionalField(
            ByteField("dst_endpoint", 10),
            lambda pkt: (pkt.frame_control.ack_req or pkt.aps_frametype == 2)
        ),
        # Group address (0/2 octets) TODO
        ConditionalField(
            # unsigned short (little-endian)
            EnumField("grp_address", 0, {}, fmt="<H"),
            lambda pkt: (pkt.frame_control.ack_req or pkt.aps_frametype == 2 \
                         or pkt.aps_frametype == 0)
        ),
        # Cluster identifier (0/2 octets)
        ConditionalField(
            # unsigned short (little-endian)
            EnumField("cluster", 0, _zcl_cluster_identifier, fmt="<H"),
            lambda pkt: (pkt.frame_control.ack_req or pkt.aps_frametype == 2 \
                         or pkt.aps_frametype == 0)
        ),
        # Profile identifier (0/2 octets)
        ConditionalField(
            EnumField("profile", 0, _zcl_profile_identifier, fmt="<H"),
            lambda pkt: (pkt.frame_control.ack_req or pkt.aps_frametype == 2 \
                         or pkt.aps_frametype == 0)
        ),
        # Source endpoint (0/1 octets)
        ConditionalField(
            ByteField("src_endpoint", 10),
            lambda pkt: (pkt.frame_control.ack_req or pkt.aps_frametype == 2 \
                         or pkt.aps_frametype == 0)
        ),
        # APS counter (1 octet)
        ByteField("counter", 0),
        # Extended header (0/1/2 octets)
        # cribbed from https://github.com/wireshark/wireshark/blob/master/epan/dissectors/packet-zbee-aps.c  # noqa: E501
        ConditionalField(
            ByteEnumField(
                "fragmentation", 0,
                {0: "none", 1: "first_block", 2: "middle_block"}),
            lambda pkt: pkt.frame_control.extended_hdr
        ),
        ConditionalField(ByteField("block_number", 0),
                         lambda pkt: pkt.fragmentation),
        # variable length frame payload:
        # 3 frame types: data, APS command, and acknowledgement
        # ConditionalField(StrField("data", ""), lambda pkt:pkt.aps_frametype == 0),  # noqa: E501
    ]


class XStrField2(StrField):
    """
    StrField which value is printed as hexadecimal.
    """

    def i2repr(self, pkt, x):
        if x is None:
            return repr(x)
        return hex_bytes(x).hex()


class ZigbeeSecurityHeader2(Packet):
    name = "Zigbee Security Header"
    fields_desc = [
        # Security control (1 octet)
        FlagsField("reserved1", 0, 2, ['reserved1', 'reserved2']),
        BitField("extended_nonce", 1, 1),  # set to 1 if the sender address field is present (source)  # noqa: E501
        # Key identifier
        BitEnumField("key_type", 1, 2, {
            0: 'data_key',
            1: 'network_key',
            2: 'key_transport_key',
            3: 'key_load_key'
        }),
        # Security level (3 bits)
        BitEnumField("nwk_seclevel", 0, 3, {
            0: "None",
            1: "MIC-32",
            2: "MIC-64",
            3: "MIC-128",
            4: "ENC",
            5: "ENC-MIC-32",
            6: "ENC-MIC-64",
            7: "ENC-MIC-128"
        }),
        # Frame counter (4 octets)
        XLEIntField("fc", 0),  # provide frame freshness and prevent duplicate frames  # noqa: E501
        # Source address (0/8 octets)
        ConditionalField(dot15d4AddressField("source", 0, adjust=lambda pkt, x: 8), lambda pkt: pkt.extended_nonce),
        # noqa: E501
        # Key sequence number (0/1 octet): only present when key identifier is 1 (network key)  # noqa: E501
        ConditionalField(ByteField("key_seqnum", 0), lambda pkt: pkt.getfieldval("key_type") == 1),  # noqa: E501
        # Payload
        # the length of the encrypted data is the payload length minus the MIC
        StrField("data", ""),  # noqa: E501
        # Message Integrity Code (0/variable in size), length depends on nwk_seclevel  # noqa: E501
        IntField("mic", ""),
    ]

    def post_dissect(self, s):
        # Get the mic dissected correctly
        mic_length = util_mic_len(self)
        if mic_length > 0:  # Slice "data" into "data + mic"
            _data, _mic = self.data[:-mic_length], self.data[-mic_length:]
            self.data, self.mic = _data, _mic
        return s
