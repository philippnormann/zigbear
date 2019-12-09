RASPBEE=pi@sniffer.local

FIRMWARE_DIR=firmware
FIRMWARE_APP=sender
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
	scp $^ ${RASPBEE}:/tmp/$(notdir $^)
	ssh ${RASPBEE} 'pip3 install --upgrade /tmp/$(notdir $^)'

remote-install:
	make remote-install-firmware
	make remote-install-python

remote-run:
	ssh ${RASPBEE} -t "bash -c 'sudo GCFFlasher_internal -r && sleep 1 && python3 -m zigbear'"


