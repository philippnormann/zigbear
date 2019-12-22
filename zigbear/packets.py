import struct
from scapy.config import conf
from scapy.layers.dot15d4 import Dot15d4Data, Dot15d4FCS
from zigbear.patch.zigbee import ZigbeeAppDataPayload, ZigbeeAppDataPayloadStub, ZigbeeNWK, ZigbeeNWKStub, ZigbeeSecurityHeader, ZigbeeClusterLibrary, ZigbeeZLLCommissioningCluster, ZLLIdentifyRequest

from zigbear.crypto import zigbee_packet_decrypt, zigbee_packet_encrypt
from zigbear.utils import pan, address, extended_address, extended_address_bytes, get_extended_source

conf.dot15d4_protocol = "zigbee"


def dot15d4_data_stub(seq_num, panid, source, destination):
    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype = 1
    dot15d4.fcf_destaddrmode = 2
    dot15d4.fcf_srcaddrmode = 2
    dot15d4.fcf_panidcompress = 1
    dot15d4.fcf_ackreq = 1
    dot15d4.seqnum = seq_num

    dot15d4_data = Dot15d4Data()
    dot15d4_data.dest_panid = panid
    dot15d4_data.dest_addr = destination
    dot15d4_data.src_addr = source

    return dot15d4 / dot15d4_data


def nwk_stub(source, destination, seqnum, extended_source=None):
    stub = ZigbeeNWK()
    stub.frametype = 0
    stub.discover_route = 1
    stub.proto_version = 2
    stub.flags = 2
    stub.destination = destination
    stub.source = source
    stub.radius = 30
    stub.seqnum = seqnum
    if extended_source is not None:
        stub.extended_source = extended_source
    return stub


def security_header_stub(extended_source, frame_counter):
    stub = ZigbeeSecurityHeader()
    stub.key_type = 1
    stub.fc = frame_counter
    stub.source = extended_source
    return stub


def encrypted_toggle(panid, source, destination, extended_source, key, frame_counter=0, seq_num=0, nwk_seq_num=0, aps_counter=0, zcl_seq_num=0):
    panid = pan(panid)
    source = address(source)
    destination = address(destination)
    extended_source = extended_address(extended_source)
    extended_source_bytes = extended_address_bytes(extended_source)

    dot15d4_data = dot15d4_data_stub(seq_num, panid, source, destination)
    nwk = nwk_stub(source, destination, nwk_seq_num)
    security_header = security_header_stub(extended_source, frame_counter)

    aps = ZigbeeAppDataPayload()
    aps.frame_control = 0
    aps.delivery_mode = 2
    aps.dst_endpoint = 255
    aps.cluster = 0x0006  # on/off cluster
    aps.profile = "HA_Home_Automation"
    aps.src_endpoint = 1

    zcl = ZigbeeClusterLibrary()
    zcl.zcl_frametype = 1  # cluster specific
    zcl.command_identifier = 0x02  # toggle
    zcl.disable_default_response = 1
    zcl.transaction_sequence = zcl_seq_num

    unencrypted_frame_part = dot15d4_data / nwk / security_header
    payload = aps / zcl

    return zigbee_packet_encrypt(key, unencrypted_frame_part, bytes(payload), extended_source_bytes)
