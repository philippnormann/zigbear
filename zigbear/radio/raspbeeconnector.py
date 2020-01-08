from zigbear.radio.connector import Connector


class RaspbeeConnector(Connector):
    def __init__(self):
        super().__init__()

    def _send(self, data):
        pass  # TODO

    def _start(self):
        pass  # TODO

    def _close(self):
        pass  # TODO

    def _set_channel(self, channel):
        pass  # TODO

    # TODO some function that call self.receive(package)
