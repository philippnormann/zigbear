import serial
import socket
import time

PORT = '/dev/ttyS0'
BAUD_RATE = 38400
TIMEOUT = 0.1

WIRESHARK_HOST = "GlaDOS.local"
WIRESHARK_PORT = 5555

TRANSPOT_KEY = bytes.fromhex('0000bc24f4942c6c6490f448082cbcbc')


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
    sock = connect_wireshark(WIRESHARK_HOST, WIRESHARK_PORT)

    while True:
        line = ser.readline().decode().strip()
        args = line.split(':')
        cmd = args[0]
        if cmd is 'R':
            print(args)
            _, length, lqi, package = args
            print(f'Recieved frame len: {length}, signal strength: {lqi}')
            package = bytes.fromhex(package)
            sock.sendto(package, (WIRESHARK_HOST, WIRESHARK_PORT))

        elif cmd is 'T':
            _, status = args
            print(f'Transmission status: {status}')

        elif cmd is 'S':
            _, channel, status = args
            print(f'Set channel {channel} status: {status}')

        elif cmd is '':
            # Raspbee is idle and waiting for commands
            ser.write(f'T:8:03086fffffffff07\n\r'.encode()) # Send beacon request as PoC
            time.sleep(0.1)
            pass

        ser.flush()


if __name__ == "__main__":
    main()
