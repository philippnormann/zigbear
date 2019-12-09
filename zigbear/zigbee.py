from scapy.layers.zigbee import Dot15d4FCS, ZigbeeNWK, ZigbeeSecurityHeader, ZigbeeAppDataPayloadStub
from zigbear.crypto import zigbee_packet_encrypt, zigbee_packet_decrypt
from zigbear.packets import extended_address_bytes, get_extended_source


def parse_frame(frame):
    pkt = Dot15d4FCS(frame)
    pkt.nwk_seclevel = 1
    pkt.data += pkt.mic
    pkt.mic = pkt.data[-4:]
    pkt.data = pkt.data[:-4]
    return pkt


def bump_counters(packet, transport_key, min_fc=0, turn_on=False):
    enc_pkt = parse_frame(packet)
    extended_source_bytes = extended_address_bytes(
        get_extended_source(enc_pkt))
    decrypted, valid = zigbee_packet_decrypt(
        transport_key, enc_pkt, extended_source_bytes)

    assert valid, 'Decryption failed!'

    aps = ZigbeeAppDataPayloadStub(decrypted)
    enc_pkt.data = ""
    enc_pkt.mic = ""
    unencrypted_frame_part = enc_pkt
    raw_aps = bytearray(aps.load)

    # bump all the counters

    # 802.15.4
    unencrypted_frame_part[Dot15d4FCS].seqnum = (
        unencrypted_frame_part[Dot15d4FCS].seqnum + 1) % 255
    # Zigbee NWK
    unencrypted_frame_part[ZigbeeNWK].seqnum = (
        unencrypted_frame_part[ZigbeeNWK].seqnum + 1) % 255
    # Zigbee Security header
    unencrypted_frame_part[ZigbeeSecurityHeader].fc = max(
        min_fc, unencrypted_frame_part[ZigbeeSecurityHeader].fc) + 1
    # Zigbee APS counter
    raw_aps[1] = (raw_aps[1] + 1) % 255
    # ZCL sequence number
    raw_aps[3] = (raw_aps[3] + 1) % 255

    if turn_on:
        raw_aps[4] = 1
    else:
        raw_aps[4] = 0

    print(
        f'802.15.4 sequence number: {unencrypted_frame_part[Dot15d4FCS].seqnum}')
    print(
        f'ZigbeeNWK sequence number: {unencrypted_frame_part[ZigbeeNWK].seqnum}')
    print(
        f'Zigbee Security header frame counter: {unencrypted_frame_part[ZigbeeSecurityHeader].fc}')
    print(f'Zigbee APS counter: {raw_aps[1]}')
    print(f'ZCL sequence number: {raw_aps[3]}')

    aps.load = raw_aps
    payload = aps.build()
    enc_pkt = zigbee_packet_encrypt(
        transport_key, unencrypted_frame_part, bytes(payload), extended_source_bytes)

    return enc_pkt.build(), unencrypted_frame_part[ZigbeeSecurityHeader].fc
