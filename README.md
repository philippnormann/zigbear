# ZigBear 🐻

Looking for some delicous ZigBee honey 🐝

## How to flash on RaspBee?

On the host, `Docker` is required for compilation of µracoli.

On the RaspberryPi, `GCFFlasher_internal` is required.

*Note*: The SSH target for the RaspBee can be configure in the `Makefile`. 

```bash
make remote-install-firmware
```

## How to run on RaspberryPi?

Requires `python3` and `pipenv` on the RaspberryPi.

```bash
make remote-install-python
make remote-run
```
