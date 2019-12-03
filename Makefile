APP = sender
FIRMWARE = ./firmware
RASPBEE = pi@sniffer.local

.PHONY: install
install:
	${FIRMWARE}/build.sh ${APP} ${FIRMWARE}/out ${RASPBEE}

.PHONY: connect
connect:
	${FIRMWARE}/connect.sh ${RASPBEE}

