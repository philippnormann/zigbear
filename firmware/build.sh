#!/usr/bin/env bash
set -e

SCRIPT_DIR=$(dirname $0)

display_usage() {
    script_name=$(basename "$0")
    echo "Usage: $script_name app out raspbee"
    echo
    echo "Build and flash custom µracoli firmware to RaspBee"
    echo
    echo "arguments:"
    echo "  app:            app to compile (e.g. sender)"
    echo "  out:            local output directory for firmware binaries"
    echo "  raspbee:        ssh destination for raspbee (e.g. pi@raspberry.local)"
}


if [[ -n "$1" ]] && [[ -n "$2" ]] && [[ -n "$3" ]]; then
    APP=$1
    OUT="$(cd $2 && pwd)"
    RASPBEE=$3
else
    display_usage
    exit 1
fi

docker build "$SCRIPT_DIR" -t uracoli-build
docker run -v "${OUT}:/tmp/out" -it uracoli-build
scp "$OUT/${APP}_raspbee.bin" "${RASPBEE}:/tmp/"
ssh "${RASPBEE}" sudo GCFFlasher_internal -f "/tmp/${APP}_raspbee.bin"
