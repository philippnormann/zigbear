RASPBEE=pi@uracoli.local
FIRMWARE_DIR=raspbee
FIRMWARE_APP=zigbear
FIRMWARE_OUT=${FIRMWARE_DIR}/out

init:
	pipenv install --dev

test:
	pipenv run pytest

run:
	pipenv run python -m zigbear

sync-pipenv-setup:
	pipenv run pipenv-setup sync

build-python:
	make init-python
	make test-python
	make sync-pipenv-setup
	pipenv run python setup.py bdist_wheel

remote-install-firmware:
	${FIRMWARE_DIR}/build.sh ${FIRMWARE_APP} ${FIRMWARE_OUT} ${RASPBEE}

remote-console:
	${FIRMWARE_DIR}/connect.sh ${RASPBEE}

remote-run:
	rsync --rsh ssh --recursive --progress --human-readable zigbear ${RASPBEE}:/tmp/
	ssh ${RASPBEE} -t "bash -c 'sudo GCFFlasher_internal -r && cd /tmp && python3 -m zigbear -c raspbee -d /dev/ttyS0'"
