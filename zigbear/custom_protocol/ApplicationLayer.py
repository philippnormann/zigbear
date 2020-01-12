import threading
from multiprocessing import Queue


class ApplicationLayer:
    class Session:
        def __init__(self, application_layer, other, port):
            self.application_layer = application_layer
            self.other = other
            self.port = port
            self.queue = Queue(1)
            application_layer.register(self)

        def send(self, data):
            self.application_layer.security_layer.send(self.other, self.port, data)

        def receive(self, timeout=30):
            return self.queue.get(True, timeout)

        def close(self):
            self.application_layer.unregister(self)

        def _receive(self, data):
            self.queue.put_nowait(data)

    class Listener:
        def __init__(self, application_layer, port, handler):
            self.application_layer = application_layer
            self.port = port
            self.handler = handler
            self.application_layer.register_listener(self)

        def _receive(self, other, data):
            session = ApplicationLayer.Session(self.application_layer, other, self.port)
            thread = threading.Thread(target=self.handler, args=(session,), daemon=True)
            thread.start()
            session._receive(data)

        def close(self):
            self.application_layer.unregister_listener(self)

    def __init__(self, security_layer):
        self.security_layer = security_layer
        self.sessions = {}
        self.listeners = {}
        self.security_layer.set_receive_callback(self.receive)

    def register(self, session):
        if session.other not in self.sessions:
            self.sessions[session.other] = {}
        self.sessions[session.other][session.port] = session

    def unregister(self, session):
        if session.other in self.sessions:
            self.sessions[session.other].pop(session.port)
            if len(self.sessions[session.other]) == 0:
                self.sessions.pop(session.other)

    def register_listener(self, listener):
        self.listeners[listener.port] = listener

    def register_unlistener(self, listener):
        self.listeners.pop(listener.port)

    def connect(self, destination, port):
        if destination == 0xFFFF:
            raise Exception("Cannot connect to broadcast")
        return ApplicationLayer.Session(self, destination, port)

    def listen(self, port, handler):
        return ApplicationLayer.Listener(self, port, handler)

    def receive(self, source, port, data):
        if source in self.sessions and port in self.sessions[source]:
            self.sessions[source][port]._receive(data)
        elif port in self.listeners:
            self.listeners[port]._receive(source, data)
