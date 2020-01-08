import serial
import socket

PORT = '/dev/ttyS0'
BAUD_RATE = 19200
TIMEOUT = 1

WIRESHARK_IP = "pop-os.local"
WIRESHARK_PORT = 5555

TRANSPOT_KEY = b'\x00\x08\xd0$\xb4\xd4\x08\xfc\xb4\xfcd\x08\xa4\xfc\xbc,'


def connect_raspbee(port: str, baudrate: int, timeout: float):
    ser = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
    inchar = ''
    while inchar != b'\n':    
        ser.write(b'\n')
        ser.flush()
        inchar = ser.read(size=1)
    print('Connection to RaspBee established!')
    return ser


def connect_wireshark(ip: str, port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return sock


def main():
    ser = connect_raspbee(PORT, BAUD_RATE, TIMEOUT)
    sock = connect_wireshark(WIRESHARK_IP, WIRESHARK_PORT)

    while True:
        inchar = ser.read(size=1)
        if len(inchar) > 0:
            length = ord(inchar)
            package = ser.read(size=length)

            print(f'Package length: {length}')
            print(f'Read bytes: {len(package)}')
            print(f'Package content: {package}')

            sock.sendto(package, (WIRESHARK_IP, WIRESHARK_PORT))


if __name__ == "__main__":
    main()
