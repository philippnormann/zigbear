#!/usr/bin/env bash
set -e -o pipefail

display_usage() {
    script_name=$(basename "$0")
    echo "Usage: $script_name raspbee"
    echo
    echo "Connect to serial console of RaspBee"
    echo
    echo "arguments:"
    echo "  raspbee:        ssh destination for raspbee (e.g. pi@raspberry.local)"
}


if [[ -n "$1" ]]; then
    RASPBEE=$1
else
    display_usage
    exit 1
fi

ssh -t "$RASPBEE" 'TERM=xterm sudo screen /dev/ttyS0 38400 && sudo pkill screen'
