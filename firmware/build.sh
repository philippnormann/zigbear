#!/usr/bin/env bash
set -eu -o pipefail

docker build . -t uracoli-build
docker run -v $(pwd)/out:/home/uracoli/out -it uracoli-build
scp out/sender_raspbee.bin pi@sniffer.local:/home/pi
ssh pi@sniffer.local 'sudo GCFFlasher_internal -f sender_raspbee.bin'