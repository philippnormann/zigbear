from zigbear.radio.connector import Connector


class MockConnector(Connector):
    def __init__(self):
        super().__init__()

    def _send(self, data):
        pass

    def _start(self):
        pass

    def _close(self):
        pass

    def _set_channel(self, channel):
        pass
