from zigbear.zigbee import bump_counters
from scapy.layers.zigbee import Dot15d4FCS, ZigbeeSecurityHeader


def test_bump_counters():
    key = b'\x00\x08\xd0$\xb4\xd4\x08\xfc\xb4\xfcd\x08\xa4\xfc\xbc,'

    packet = b"\x41\x88\x4f\x03\xae\xff\xff\x00\x00\x08\x02\xfd\xff\x00\x00\x0a" \
             b"\xd8\x28\xc5\x57\x00\x00\x6a\xfe\x03\xff\xff\x2e\x21\x00\x00\x7c" \
             b"\xbe\x79\x42\x58\xe3\x2a\xf7\xb4\x88\x89\x7b\xc2\x90\x9a\x4d\xac\xbf"

    new_packet, _ = bump_counters(packet, key)

    old_sec_fc = Dot15d4FCS(packet)[ZigbeeSecurityHeader].fc
    new_sec_fc = Dot15d4FCS(new_packet)[ZigbeeSecurityHeader].fc

    assert old_sec_fc + 1 == new_sec_fc
