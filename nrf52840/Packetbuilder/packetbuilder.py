from scapy.layers.zigbee import *
from scapy.layers.dot15d4 import *
from Packetbuilder.scapy_adjustments import *
from Packetbuilder.crypto import *

#Encrypt the APS with CCM
def ccm_encrypt_APS(frame_counter, extended_source, sec_ctr, key, ZAPS_Frame):
    #TODO actual CCM encryption using src_address + frame_counter + sec_ctr
    return ZAPS_Frame.build()

#ZigBee Cluster Library Frame
def build_philips_ZCL(turn_on, sequence_number):
    ZCL = ZigbeeClusterLibrary(zcl_frametype=0x1, manufacturer_specific=0x0,\
            direction=0x0, disable_default_response=0x1,\
            transaction_sequence=sequence_number)
    if turn_on:
        ZCL.command_identifier = 0x01
    else:
        ZCL.command_identifier = 0x40
        ZCL = ZCL / ZCLGeneralReadAttributes(attribute_identifiers=0x00)
    return ZCL

#ZigBee Application Support Layer Data
def build_philips_ZAPS(group, source_endpoint, counter, ZCL_Frame):
    ZADP = ZigbeeAppDataPayload2(frame_control=0x0, delivery_mode=0x3,\
            aps_frametype=0x0, grp_address=group, cluster=0x0006,\
            profile=0x0104, src_endpoint=source_endpoint, counter=counter)
    return ZADP / ZCL_Frame

#ZigBee Security Header
def build_philips_ZSH(frame_counter, extended_source, mic, key_seq, key,\
                        ZAPS_Frame):
    ZSH = ZigbeeSecurityHeader2(extended_nonce=1, key_type=0x1,\
            fc=frame_counter, source=extended_source, key_seqnum=key_seq,\
            mic=mic)
    ZSH.data = ccm_encrypt_APS(frame_counter, extended_source, 0x28, key,\
                                ZAPS_Frame)
    return ZSH

#ZigBee Network Layer Data
def build_philips_ZNWKD(source, radius, sequence_number, ZSH_Frame):
    ZNWKD = ZigbeeNWK(discover_route=0x0, proto_version=0x2, frametype=0x0,\
            flags=0x2, destination=0xfffd, source=source, radius=radius,\
            seqnum=sequence_number)
    return ZNWKD / ZSH_Frame

#IEEE 802.15.4 Data
def build_15dot4_Data(source, PAN, sequence_number, ZNWKD_Frame):
    IEEE_fc = Dot15d4(fcf_reserved_1=0, fcf_panidcompress=1, fcf_ackreq=0,\
                fcf_pending=0, fcf_security=0, fcf_frametype=0x1,\
                fcf_srcaddrmode=0x2, fcf_framever=0x0, fcf_destaddrmode=0x2,\
                fcf_reserved_2=0x0, seqnum=sequence_number)
    IEEE_data = Dot15d4Data(dest_panid=PAN, dest_addr=0xffff, src_addr=source)
    return IEEE_fc / IEEE_data / ZNWKD_Frame

#Build a frame that should work with Philips Hue to turn a lamp on or off
def create_philips_onoff_testframe(source, extended_source, PAN,\
                                    dot15d4_sequence_number, ZNWK_radius,\
                                    ZNWK_sequence_number, ZSH_frame_counter,\
                                    ZSH_mic, ZSH_key_seqnum, ZSH_key,\
                                    ZAPS_group, ZAPS_src_endpoint,\
                                    ZAPS_counter, ZCL_on, ZCL_sequence_number):
    ZCL = build_philips_ZCL(ZCL_on, ZCL_sequence_number)
    ZAPS = build_philips_ZAPS(ZAPS_group, ZAPS_src_endpoint, ZAPS_counter, ZCL)
    ZSH = build_philips_ZSH(ZSH_frame_counter, extended_source, ZSH_mic,\
                            ZSH_key_seqnum, ZSH_key, ZAPS)
    ZNWDK = build_philips_ZNWKD(source, ZNWK_radius, ZNWK_sequence_number, ZSH)
    dot15dot4 = build_15dot4_Data(source, PAN, dot15d4_sequence_number, ZNWDK)
    data, mic = zigbee_packet_encrypt(ZSH_key.to_bytes(16, byteorder='big'),\
                                    dot15dot4, ZAPS.build(), extended_source)
    dot15dot4[ZigbeeSecurityHeader2].data = data
    dot15dot4[ZigbeeSecurityHeader2].mic = int.from_bytes(mic, "big")
    return dot15dot4

#Example frame
def create_example_frame(frame_counter, onoff):
    return create_philips_onoff_testframe(0x9752, 0x00178801050130e7, 0x4625,\
                                            73, 30, 56, frame_counter,\
                                            0xe5b6dd38, 0,\
                                            0xaffe0000000000000000000000000000,\
                                            0x4ebf, 64, 181, onoff, 165)

def create_valid_complete_packet(frame):
    # Only for creating fully valid packets to analyze with Wireshark, should
    # usually be added by the device
    filler_tap = b'\x00\x00\x1c\x00\x01\x00\x04\x00\x00\x00\x58\xc2\x03\x00'\
                    b'\x03\x00\x0f\x00\x00\x00\x0a\x00\x01\x00\xa0\x00\x00\x00'
    return filler_tap + frame.build()
