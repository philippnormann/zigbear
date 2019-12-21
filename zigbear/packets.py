from scapy.config import conf
from scapy.layers.dot15d4 import Dot15d4Data, Dot15d4FCS
from zigbear.patch.zigbee import ZigbeeAppDataPayload, ZigbeeAppDataPayloadStub, ZigbeeNWK, ZigbeeSecurityHeader, ZigbeeClusterLibrary

from zigbear.crypto import zigbee_packet_decrypt, zigbee_packet_encrypt
from zigbear.utils import pan, address, extended_address, extended_address_bytes, get_extended_source

conf.dot15d4_protocol = "zigbee"


def dot15d4_data_stub(seq_num, panid, source, destination):
    dot15d4 = Dot15d4FCS()
    dot15d4.fcf_frametype=1
    dot15d4.fcf_destaddrmode=2
    dot15d4.fcf_srcaddrmode=2
    dot15d4.fcf_panidcompress=1
    dot15d4.fcf_ackreq=1
    dot15d4.seqnum=seq_num

    dot15d4_data = Dot15d4Data()
    dot15d4_data.dest_panid=panid
    dot15d4_data.dest_addr=destination
    dot15d4_data.src_addr = source

    return dot15d4 / dot15d4_data


def nwk_stub(source, destination, seqnum, extended_source=None):
    stub = ZigbeeNWK()
    stub.frametype=0
    stub.discover_route=1
    stub.proto_version=2
    stub.flags=2
    stub.destination=destination
    stub.source=source
    stub.radius=30
    stub.seqnum=seqnum
    if extended_source is not None:
        stub.extended_source=extended_source
    return stub


def security_header_stub(extended_source, frame_counter):
    stub = ZigbeeSecurityHeader()
    stub.key_type=1
    stub.fc=frame_counter
    stub.source=extended_source
    return stub


def encrypted_toggle(panid, source, destination, extended_source, key, frame_counter=0, seq_num=0, nwk_seq_num=0, aps_counter=0, zcl_seq_num=0):
    panid = pan(panid)
    source = address(source)
    destination = address(destination)
    extended_source = extended_address(extended_source)

    extended_source_bytes = extended_address_bytes(extended_source)

    aps_payload = bytearray(b"\x0c\x02\x00\x06\x00\x04\x01\x01\xf4\x11\x9c\x02")
    # bump Zigbee APS counter
    #aps_payload[7] = aps_counter
    # bump ZCL sequence number
    #aps_payload[9] = zcl_seq_num
    # set command to toggle
    #aps_payload[10] = 2

    dot15d4_data = dot15d4_data_stub(seq_num, panid, source, destination)
    nwk = nwk_stub(source, destination, nwk_seq_num)
    security_header = security_header_stub(extended_source, frame_counter)
    unencrypted_frame_part = dot15d4_data / nwk / security_header

    return zigbee_packet_encrypt(key, unencrypted_frame_part, bytes(aps_payload), extended_source_bytes)


def parse_frame(frame):
    pkt = Dot15d4FCS(frame)
    pkt.nwk_seclevel = 5
    pkt.data += pkt.mic
    pkt.mic = pkt.data[-4:]
    pkt.data = pkt.data[:-4]
    return pkt


def bump_counters(parsed_frame, decrypted_payload, min_fc=0):
    aps_packet = ZigbeeAppDataPayloadStub(decrypted_payload)
    aps_load = bytearray(aps_packet.load)

    parsed_frame.data = ""
    parsed_frame.mic = ""

    # bump 802.15.4 sequene number
    parsed_frame[Dot15d4FCS].seqnum = (parsed_frame[Dot15d4FCS].seqnum + 1) % 255
    # bump Zigbee NWK sequene number
    parsed_frame[ZigbeeNWK].seqnum = (parsed_frame[ZigbeeNWK].seqnum + 1) % 255
    # bump Zigbee Security header frame counter
    parsed_frame[ZigbeeSecurityHeader].fc = max(min_fc, parsed_frame[ZigbeeSecurityHeader].fc) + 1
    # bump Zigbee APS counter
    aps_load[1] = (aps_load[1] + 1) % 255
    # bump ZCL sequence number
    aps_load[3] = (aps_load[3] + 1) % 255
    # set command to toggle
    aps_load[4] = 2

    print(f'802.15.4 sequence number: {parsed_frame[Dot15d4FCS].seqnum}')
    print(f'ZigbeeNWK sequence number: {parsed_frame[ZigbeeNWK].seqnum}')
    print(f'Zigbee Security header frame counter: {parsed_frame[ZigbeeSecurityHeader].fc}')
    print(f'Zigbee APS counter: {aps_load[1]}')
    print(f'ZCL sequence number: {aps_load[3]}')

    aps_packet.load = aps_load
    new_payload = aps_packet.build()

    return parsed_frame, new_payload
