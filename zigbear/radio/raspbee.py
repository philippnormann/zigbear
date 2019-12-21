import serial, time

MAX_PACKET_LENGTH = 255

def send_packet(ser: serial.Serial, packet: bytearray):
    packet_len = len(packet)
    print(ser.readline())
    if packet_len > MAX_PACKET_LENGTH:
        print(f'Packet is too big, {packet_len} > {MAX_PACKET_LENGTH}')
    else:
        ser.write([packet_len])
        print(ser.readline())
        ser.write(packet)
        print(ser.readline())
        print(ser.readline())
