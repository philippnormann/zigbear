from Packetbuilder.packetbuilder import create_valid_complete_packet, create_example_frame

test = b"\00" * 68


def to_hex_dump(bytes):
    offset = 0
    f = open("dump.hex", "w")
    for part in range(0, len(bytes), 16):
        hexpart = bytes[part:part + 16].hex()
        hexpart = ' '.join(a + b for a, b in zip(hexpart[::2], hexpart[1::2]))
        f.write(format(offset, '#06x')[2:6] + "  " + hexpart + "\n")
        offset += 16
    f.close()


to_hex_dump(create_valid_complete_packet(create_example_frame()))
