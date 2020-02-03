import argparse
import logging
import logging.config

from zigbear.radio.cc2531connector import CC2531Connector
from zigbear.radio.nrfconnector import NrfConnector
from zigbear.radio.raspbeeconnector import RaspbeeConnector
from zigbear.radio.socketconnector import SocketConnector
from zigbear.zigbear import main


def arg_parser():
    debug_choices = ('DEBUG', 'INFO', 'WARN', 'ERROR')
    connector_choices = ('nrf', 'cc2531', 'raspbee', 'socket')

    parser = argparse.ArgumentParser(add_help=True, description='Zigbear...')

    log_group = parser.add_argument_group('Logging')
    log_group.add_argument('-L', '--log-file', action='store', nargs='?',
                           const='zigbear.log', default=False,
                           help='Log output in LOG_FILE. If -L is specified \
                                       but LOG_FILE is omitted, %s will be used. \
                                       If the argument is omitted altogether, \
                                       logging will not take place at all.'
                                % ('zigbear.log',))

    log_group.add_argument('-l', '--log-level', action='store',
                           choices=debug_choices,
                           default='INFO',
                           help='Log messages of severity LOG_LEVEL or \
                                       higher. Only makes sense if -L is also \
                                       specified (Default %s)'
                                % ('INFO',))

    zigbear_group = parser.add_argument_group('Zigbear')
    zigbear_group.add_argument('-c', '--connector', action='store',
                               choices=connector_choices,
                               default=False,
                               help='Configure a Connector')

    zigbear_group.add_argument('-d', '--device', action='store',
                               default='/dev/ttyACM0',
                               help='Read/Send from device DEVICE \
                                      (Default: %s)' % ('/dev/ttyACM0',))

    zigbear_group.add_argument('-C', '--channel', action='store',
                               default=25,
                               help='The Radio Channel for listening and sending \
                                          (Default: %d)' % (25,))

    zigbear_group.add_argument('-w', '--wireshark-host', action='store',
                               default='127.0.0.1',
                               help='The wireshark host \
                                              (Default: %s)' % ('127.0.0.1',))

    zigbear_group.add_argument('-r', '--receive-port', action='store',
                               default=8080,
                               help='The receive port for the socket connector \
                                              (Default: %d)' % (8080,))

    zigbear_group.add_argument('-t', '--target-port', action='store',
                               default=9090,
                               help='The target port for the socket connector \
                                              (Default: %d)' % (9090,))
    return parser.parse_args()


def log_init():
    if args.log_file is not False:
        logging.basicConfig(filename=args.log_file, format='%(asctime)s - %(levelname)8s - %(message)s',
                            level=args.log_level)


def connector_init():
    port = args.device
    connector_string = args.connector
    if connector_string == 'nrf':
        return NrfConnector(port)
    elif connector_string == 'cc2531':
        return CC2531Connector(port)
    elif connector_string == 'raspbee':
        host = args.wireshark_host
        return RaspbeeConnector(port=port, wireshark_host=host)
    elif connector_string == 'socket':
        receive_port = args.receive_port
        target_port = args.target_port
        return SocketConnector(receive_port=receive_port, target_port=target_port)


if __name__ == '__main__':
    args = arg_parser()
    log_init()
    connector = None
    if args.connector:
        connector = connector_init()
        connector.set_channel(args.channel)
    main(connector)
