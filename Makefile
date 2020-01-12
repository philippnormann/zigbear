RASPBEE=pi@uracoli.local

FIRMWARE_DIR=raspbee
FIRMWARE_APP=zigbear
FIRMWARE_OUT=${FIRMWARE_DIR}/out

remote-install-firmware:
	${FIRMWARE_DIR}/build.sh ${FIRMWARE_APP} ${FIRMWARE_OUT} ${RASPBEE}

remote-console:
	${FIRMWARE_DIR}/connect.sh ${RASPBEE}

init-python:
	pipenv install --dev

test-python:
	pipenv run pytest

sync-pipenv-setup:
	pipenv run pipenv-setup sync

build-python:
	make init-python
	make test-python
	make sync-pipenv-setup
	pipenv run python setup.py bdist_wheel

remote-install-python: dist/*.whl
	make build-python
	scp $^ ${RASPBEE}:/tmp/$(notdir $^)
	ssh ${RASPBEE} 'pip3 install --upgrade /tmp/$(notdir $^)'

remote-install:
	make remote-install-firmware
	make remote-install-python

remote-run:
	ssh ${RASPBEE} -t "bash -c 'sudo GCFFlasher_internal -r && python3 -m zigbear'"

remote-run-dev:
	rsync --rsh ssh --recursive --progress --human-readable zigbear ${RASPBEE}:/tmp/
	ssh ${RASPBEE} -t "bash -c 'sudo GCFFlasher_internal -r && cd /tmp/zigbear && python3 -m old.main'"
