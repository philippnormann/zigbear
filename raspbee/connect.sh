#!/usr/bin/env bash
set -e -o pipefail

display_usage() {
    script_name=$(basename "$0")
    echo "Usage: $script_name raspbee port baudrate"
    echo
    echo "Connect to serial console of RaspBee"
    echo
    echo "arguments:"
    echo "  raspbee:        ssh destination for raspbee (e.g. pi@raspberry.local)"
    echo "  port:           serial port on raspberry (default: /dev/ttyS0)"
    echo "  baudrate:       ssh destination for raspbee (default: 38400)"
}

if [[ -n "$1" ]]; then
    RASPBEE=$1
else
    display_usage
    exit 1
fi

if [[ -n "$2" ]]; then
    PORT=$1
else
    PORT=/dev/ttyS0
fi

if [[ -n "$3" ]]; then
    BAUD_RATE=$3
else
    BAUD_RATE=38400
fi

ssh -t "$RASPBEE" "TERM=xterm sudo GCFFlasher_internal -r && sleep 1 && \
                              sudo screen $PORT $BAUD_RATE && \
                              sudo pkill screen"
