class SecurityLayer:
    def __init__(self, networkLayer):
        self.networkLayer = networkLayer

    def receive(self, source, port, data):
        pass
