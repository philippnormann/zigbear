#!/usr/bin/env bash
set -eu -o pipefail

ssh -t pi@sniffer.local 'TERM=xterm sudo screen /dev/ttyS0 38400 && sudo pkill screen'