#!/usr/bin/env bash
set -eu -o pipefail
echo "Extracting firmware binaries..."
cd install/bin
HEX_FILES="*.hex"
for f in $HEX_FILES
do
  name=$(basename "$f" | cut -f 1 -d '.')
  echo "Converting $name.hex to $name.bin"
  avr-objcopy -I ihex -O binary "$name.hex" "$name.bin"
  cp "$name.bin" ~/out
done
