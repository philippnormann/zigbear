from zigbear.zigbear import main
import argparse
import logging
import logging.config

def arg_parser():
    debug_choices = ('DEBUG', 'INFO', 'WARN', 'ERROR')

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

    return parser.parse_args()

def log_init():
    if args.log_file is not False:
        logging.basicConfig(filename=args.log_file, format='%(asctime)s - %(levelname)8s - %(message)s', level=args.log_level)

if __name__ == "__main__":
    args = arg_parser()

    log_init()

    main()
