# ZigBear 🐻

A Zigbee security research toolkit for the [RaspBee](https://phoscon.de/en/raspbee), [nRF52840](https://www.nordicsemi.com/Products/Low-power-short-range-wireless/nRF52840) and [CC2531](https://www.ti.com/product/CC2531) radio modules.

In order to develop and test improved network join procedures using asymmetric encryption, a custom proof of concept protocol based on the IEEE 802.15.4 standard was developed and is also included in the toolkit.

## Flashing the firmware
The radio modules need to be flashed with our custom firmware, prior to using it with ZigBear.

The instructions, on how to do this, vary depending on the chosen transceiver.

### RaspBee

To remotely flash the firmware of a RaspBee module, execute

```bash
$ make remote-install-firmware
```
On the host, `docker` is required for compilation of [µracoli](http://uracoli.nongnu.org/).

On the RaspberryPi, `GCFFlasher_internal` is required (included in the installation of [deCONZ](https://www.phoscon.de/en/raspbee/install#raspbian)).

The SSH target for the RaspBee can be configure in the `Makefile`. 

### nRF52840

To flash a nRF52840 dongle, the [nRF Connect](https://www.nordicsemi.com/Software-and-tools/Development-Tools/nRF-Connect-for-desktop#infotabs) software is required.

Detailed instructions on how to flash using nRF Connect, can be found [here](https://infocenter.nordicsemi.com/topic/ug_nc_programmer/UG/nrf_connect_programmer/ncp_programming_dongle.html).

### CC2531

To flash a CC2531 dongle, the [CC Debugger](http://www.ti.com/tool/CC-DEBUGGER) from Texas Instruments is required. 

Detailed instructions on how to flash using  the  CC Debugger can be found [here](https://www.zigbee2mqtt.io/getting_started/flashing_the_cc2531.html).


## Launching ZigBear

To launch the ZigBear Python CLI locally, simply execute
```bash
$ make run
```
Requires `python3`, `pipenv` and optionally `tkinter` for the virtual lamp 

### Remote execution on RaspberryPi

To remotely execute ZigBear via SSH on a RaspberryPi + RaspBee, execute

```bash
$ make remote-run
```

Requires `python3` and `pipenv` on the RaspberryPi.

## Usage
The ZigBear CLI can be either preconfigured using command line arguments 
```bash
usage: __main__.py [-h] [-L [LOG_FILE]] [-l {DEBUG,INFO,WARN,ERROR}]
                   [-c {nrf,cc2531,raspbee,socket}] [-d DEVICE] [-C CHANNEL]
                   [-w WIRESHARK_HOST] [-r RECEIVE_PORT] [-t TARGET_PORT]

ZigBear CLI

optional arguments:
  -h, --help            show this help message and exit

Logging:
  -L [LOG_FILE], --log-file [LOG_FILE]
                        Log output to LOG_FILE. If -L is specified but
                        LOG_FILE is omitted, "zigbear.log" will be used. If
                        the argument is omitted altogether, logging will not
                        take place at all.
  -l {DEBUG,INFO,WARN,ERROR}, --log-level {DEBUG,INFO,WARN,ERROR}
                        Log messages of severity LOG_LEVEL or higher. Only
                        makes sense if -L is also specified (Default: INFO)

ZigBear:
  -c {nrf,cc2531,raspbee,socket}, --connector {nrf,cc2531,raspbee,socket}
                        configure connector type
  -d DEVICE, --device DEVICE
                        transceive from DEVICE (Default: /dev/ttyACM0)
  -C CHANNEL, --channel CHANNEL
                        radio channel for listening and sending (Default: 25)
  -w WIRESHARK_HOST, --wireshark-host WIRESHARK_HOST
                        wireshark host (Default: 127.0.0.1)
  -r RECEIVE_PORT, --receive-port RECEIVE_PORT
                        receive port for the socket connector (Default: 8080)
  -t TARGET_PORT, --target-port TARGET_PORT
                        target port for the socket connector (Default: 9090)

```
or interactively configured using the CLI commands after launching ZigBear

### Select a connector
To select the connector for your hardware, execute
```
connector <connector> 
```

`<connector>` must be one of the following options:

- nrf
- cc2531
- raspbee
- socket

### Select a channel
After selecting a connector you can choose a radio channel
```
channel <number>
```

`<number>` must be between and including 11 and 25.

### Send raw data
With the selected channel you can now start to transmit raw data (hexadecimal string) using the `send` command
```
send <hexadecimalString>
```

## Custom protocol
An application communicates with our custom protocol stack, which consists of the following layers. 

![Protocol Stack](diagramms/Structure%20Zigbear%20Stack.png)

The MAC Layer communicates via one of the connectors with the hardware and vice versa. 

### MAC Layer
The MAC layer of the IEEE 802.15.4 protocol is used. This layer sends and receives data directly using one of the radio connectors.

### Network Layer
The Network Layer has several tasks. One is the partitioning of packages which exceed the maximum size of 80 byte. Another task is to send ACK packages. A retry mechanism is implemented to send packages again if no response was received.

### Security Layer
The Security Layer handles encryption and decryption of packages.

For the encryption and decryption of packets, that are exchanged between devices that share a network key, the symmetric encoding AES-GCM is used. Advanced Encryption Standard (AES) is a block cipher which decodes 16 byte blocks with byte substitution, permutations and transformations. For these operations a key with a length of 128, 192 or 256 Bit is used.

As AES-GCM is an authenticated encryption algorithm, it is also capable of providing integrity via the authentication tag, that is produced as a result of it. If an encrypted message has an invalid authentication tag, it will not be decrypted or relayed to the application layer.

To exchange the network key the Elliptic Curve Diffie-Hellman (ECDH) algorithm is used. The communication partners exchange their public keys and calculate a shared key using their private keys. This shared key is passed through HKDF to turn it into a cryptographically stronger key.

![Key Exchange](diagramms/Zigbear%20Key%20Exchange.png)

The exchange of the actual network key is encrypted using the key derived from the shared key. This secure channel could also be used for negotiating different details of the connection in the future. After the network key is exchaged, any keys relating to that exchange are dropped by both communication partners. A new set of keys has to be generated for each exchange, thus providing forward secrecy for key exchanges.


### Application Layer
The Application Layer offers a socket interface for the development of high level applications. It consists of a Session and a Listener class where Session has methods to send a network key and a initiation package and Listener has methods to register and connect to a broadcast. Both can send and receive packages.

## Example application

The projects comes with a virtual lamp as an example application for our custom protocol. By sending messages between two ZigBear instances, where one acts as device and the other one as coordinator, the "lamp" (a colored GUI window) can be switched off, on or set to specific brightness values.

To test the lamp in combination with a coordinator, follow these steps:
- Launch two instances of ZigBear from the project directory with 
```
$ make run
```
- Use UDP connector (`socket`), for simplicity.
- Enter inverse send and receive ports on the two clients.
- Launch one client into `device` mode and the other into `coordinator` mode.
- Enter `info` on the device client to display its random address (in the following steps named as `<device_address>`).
- Perform the following commands on the coordinator client to pair it with the device client.
```
initiate <device_address> 
sendkey <device_address>
```
- Start the virtual lamp example application on the device client with the command `lamp`
- Control the lamp by sending on of the following commands from the coordinator client to the device client:
```
toggle <device_address>
brightness <device_address> <brightness>
```


## Future enhancements
Development of ZigBear is on-going, and there is still much to do.

Some of the things that could be interesting to work on, in no particular order, are listed below:

- [ ] ZigBee Light Link attacks
- [ ] Automated network join attacks
- [ ] Remote factory reset attacks
- [ ] Remote firmware update attacks
- [ ] Formal verification of custom protocol
- [ ] Authorization for custom protocol

## Resources

- [All Your Bulbs Are Belong to Us: Investigating the Current State of Security in Connected Lighting Systems](https://arxiv.org/pdf/1608.03732.pdf)
- [IoT Goes Nuclear: Creating a ZigBee Chain Reaction](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7958578)
- [Hacking Intelligent Building](https://conference.hitb.org/hitbsecconf2018ams/materials/D1T2%20-%20YuXiang%20Li,%20HuiYu%20Wu%20&%20Yong%20Yang%20-%20Hacking%20Intelligent%20Buildings%20-%20Pwning%20KNX%20&%20ZigBee%20Networks.pdf)
- [Security Analysis of Zigbee](https://courses.csail.mit.edu/6.857/2017/project/17.pdf)
- [ZigBee Exploited - The Good, the Bad and the Ugly (Paper)](https://www.blackhat.com/docs/us-15/materials/us-15-Zillner-ZigBee-Exploited-The-Good-The-Bad-And-The-Ugly-wp.pdf)
- [ZigBee Exploited - The Good, The Bad and The Ugly (Video)](https://www.youtube.com/watch?v=9xzXp-zPkjU)
- [Improved Secure ZigBee Light Link Touchlink Commissioning Protocol Design](https://ieeexplore.ieee.org/document/8418123)

## Inspirations

- [KillerBee](https://github.com/riverloopsec/killerbee)
- [ZigDiggity](https://github.com/BishopFox/zigdiggity)
- [SecBee](https://github.com/Cognosec/SecBee)
- [Z3sec](https://github.com/IoTsec/Z3sec)
- [Hue Thief](https://github.com/vanviegen/hue-thief)
