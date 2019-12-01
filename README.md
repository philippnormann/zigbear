# ZigBear 🐻

Looking for some delicous ZigBee honey 🐝

## How to compile?
Use `Dockerfile` including the AVR-Toolchain, required for compiling the µracoli firmware and our own programs.
1. Build docker image using
    
    `docker build . -t uracoli`

2. Run docker image with a volume (located at `./out`) for persisting compiled results

    `docker run -v $(pwd)/out:/home/uracoli/work/ -it uracoli`

3. Compile your firmware and copy resulting binary to `/home/uracoli/work/out`

## How to flash?
1. Copy your firmware to the RaspberryPi using `scp`

2. `ssh` into RaspberyPi and run `GCFlasher_internal -f firmware.bin`

## How to run?

???