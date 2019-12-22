import sys
import time
import serial
from zigbear.radio.raspbee import send_packet
from zigbear.packets import encrypted_toggle

SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 38400
TIMEOUT = 10

TRANSPOT_KEY = b'\x00\x08\xd0$\xb4\xd4\x08\xfc\xb4\xfcd\x08\xa4\xfc\xbc,'


def main():
    panid = 0xae03
    source = 0x0000
    destination = 0xffff
    extended_source = 0x00212effff03fe6a  # Extended Source: Dresden-_ff:ff:03:fe:6a

    frame_counter = 25055
    seq_num = 0
    nwk_seq_num = 0
    aps_counter = 0
    zcl_seq_num = 0

    ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)
    ser.write(b'\n')

    while True:
        input("Enter to toggle lamp: ")

        frame = encrypted_toggle(panid, source, destination, extended_source,
                                 TRANSPOT_KEY, frame_counter=frame_counter,
                                 seq_num=seq_num, nwk_seq_num=nwk_seq_num,
                                 aps_counter=aps_counter, zcl_seq_num=zcl_seq_num).build()

        send_packet(ser, frame[:-2])
        print(f'Frame counter: {frame_counter}')

        frame_counter += 1
        seq_num = (seq_num + 1) % 256
        nwk_seq_num = (nwk_seq_num + 1) % 256
        aps_counter = (aps_counter + 1) % 256
        zcl_seq_num = (zcl_seq_num + 1) % 256

if __name__ == "__main__":
    main()
