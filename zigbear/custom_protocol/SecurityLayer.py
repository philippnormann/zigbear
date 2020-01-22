import secrets

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

from zigbear.custom_protocol.scapy_layers import ZigbearSecurityLayer


class SecurityLayer:
    def __init__(self, networkLayer, network_key=None):
        self.networkLayer = networkLayer
        self.framecount = secrets.randbelow(2 ** 32)
        self.key_cache = {}
        self.framecount_cache = {}
        # Can and should be none for non-coordinators (has to be 128, 192 or 256 bit)
        self.network_key = network_key
        self.receive_callback = lambda source, port, data: source
        self.networkLayer.set_receive_callback(self.receive)

    def new_framecount(self):
        s = self.framecount
        self.framecount = (self.framecount + 1) % 2 ** 32
        return s

    def check_framecount(self, source, framecount):
        if source in self.framecount_cache:
            result = self.framecount_cache[source] < framecount
        else:
            self.framecount_cache[source] = framecount
            result = True
        return result

    def set_source_framecount(self, source, framecount):
        self.framecount_cache[source] = framecount

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def enable_pairing_mode(self):
        self.network_key = None

    def make_security_packet(self, data):
        try:
            sec = ZigbearSecurityLayer(data)
        except:
            sec = None
        return sec

    def receive(self, source, port, data):
        sec = self.make_security_packet(data)
        if sec:
            applayer_data = None
            if self.check_framecount(source, sec.fc):
                if sec.message_type == 0:
                    applayer_data = sec.data
                elif sec.message_type == 1:
                    self.handle_pairing_request(source, port, sec.data, sec.flags & 1)
                elif sec.message_type == 2 and not self.network_key:
                    self.handle_network_key(source, sec.fc, sec.data, sec.mac)
                else:
                    applayer_data = self.handle_encrypted_data(source, sec.fc, sec.data, sec.mac)
                if applayer_data:
                    self.receive_callback(source, port, applayer_data)

    def handle_pairing_request(self, source, port, secdata, reply):
        self.generate_public_key(source)
        peer_public_key = self.deserialize_public_key(secdata)
        self.key_cache[source]["peer_public_key"] = peer_public_key
        self.generate_derived_keys(source, peer_public_key, b"test")
        if reply:
            self.send(source, port, self.serialize_public_key(self.key_cache[source]["public_key"]), 1, 0)

    def handle_network_key(self, source, framecount, secdata, mac):
        error, network_key = self.decryption(framecount, secdata, mac, source, True)
        if not error:
            self.network_key = network_key
            self.key_cache.pop(source, None)
            self.set_source_framecount(source, framecount)

    def handle_encrypted_data(self, source, framecount, secdata, mac):
        error, applayer_data = self.decryption(framecount, secdata, mac, source)
        if not error:
            self.set_source_framecount(source, framecount)
            return applayer_data

    def send(self, destination, port, data, message_type=3, flags=0):
        packet = ZigbearSecurityLayer(flags=flags, message_type=message_type, fc=self.new_framecount())
        packet_data = mac = None
        if message_type == 0:
            packet.data = data
        elif message_type == 1:
            packet.data = self.handle_prepare_pk(destination)
        elif message_type == 2:
            packet.data, packet.mac = self.handle_prepare_nwk(destination, packet.fc)
        else:
            packet.data, packet.mac = self.handle_prepare_encdata(destination, packet.fc, data)
        self.networkLayer.send(destination, port, packet)

    def handle_prepare_pk(self, destination):
        self.generate_public_key(destination)
        return self.serialize_public_key(self.key_cache[destination]["public_key"])

    def handle_prepare_nwk(self, destination, framecount):
        return self.encryption(framecount, self.network_key, destination, True)

    def handle_prepare_encdata(self, destination, framecount, data):
        return self.encryption(framecount, data.build(), destination)

    def get_connection_attempts(self):
        return list(self.key_cache.keys())

    def generate_public_key(self, source):
        if source not in self.key_cache or "public_key" not in self.key_cache[source]:
            self.key_cache[source] = {}
            new_private_key = ec.generate_private_key(ec.SECP224R1(), default_backend())
            self.key_cache[source]["public_key"] = new_private_key.public_key()
            self.key_cache[source]["private_key"] = new_private_key

    def serialize_public_key(self, public_key):
        return public_key.public_bytes(encoding=serialization.Encoding.DER,
                                       format=serialization.PublicFormat.SubjectPublicKeyInfo)

    def deserialize_public_key(self, serialized_key):
        return serialization.load_der_public_key(serialized_key, backend=default_backend())

    def generate_derived_keys(self, source, peer_public_key, salt):
        shared_key = self.key_cache[source]["private_key"].exchange(ec.ECDH(), peer_public_key)
        self.key_cache[source]["shared_encryption_key"] = self.derive_key(b"encryption key", salt, shared_key)

    def derive_key(self, info, salt, shared_key):
        return HKDF(algorithm=hashes.SHA256(), length=32, salt=salt, info=info,
                    backend=default_backend()
                    ).derive(shared_key)

    def get_nonce(self, framecount, destination):
        return framecount.to_bytes(4, byteorder='big')

    def encryption(self, framecount, data, destination, shared=False):
        key = self.key_cache[destination]["shared_encryption_key"] if shared else self.network_key
        nonce = self.get_nonce(framecount, destination)
        aesgcm = AESGCM(key)
        sk_encrypted = aesgcm.encrypt(nonce, data, None)
        return (sk_encrypted[:-16], int.from_bytes(sk_encrypted[-16:], 'big'))

    def decryption(self, framecount, data, mac, source, shared=False):
        key = self.key_cache[source]["shared_encryption_key"] if shared else self.network_key
        if shared:
            self.key_cache.pop(source, None)
        nonce = self.get_nonce(framecount, source)
        aesgcm = AESGCM(key)
        error = result = None
        try:
            result = aesgcm.decrypt(nonce, data + mac.to_bytes(16, 'big'), None)
        except:
            error = 1
        return (error, result)
