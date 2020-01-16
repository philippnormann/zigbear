import math

from zigbear.custom_protocol.NegotiationLayer import ZigbearSecurityLayer
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SecurityLayer:
    def __init__(self, networkLayer, network_key=None):
        self.networkLayer = networkLayer
        self.framecount = 0
        self.key_cache = {}
        # Can and should be none for non-coordinators
        self.network_key = b"network_keynetwork_keynetwork_ke"
        self.receive_callback = lambda source, port, data: source
        self.networkLayer.set_receive_callback(self.receive)

    def new_framecount(self):
        s = self.framecount
        self.framecount = (self.framecount + 1) % math.pow(2, 32)
        return s

    def set_receive_callback(self, callback):
        self.receive_callback = callback

    def enable_pairing_mode(self):
        self.network_key = None

    def receive(self, source, port, data):
        sec = ZigbearSecurityLayer(data)
        secdata = sec.data
        message_type = sec.message_type
        applayer_data = None
        if message_type == 0:
            applayer_data = secdata
        elif message_type == 1:
            peer_public_key = self.deserialize_public_key(secdata)
            self.key_cache[source]["peer_public_key"] = peer_public_key
            if "public_key" not in self.key_cache[source]:
                self.generate_public_key(source)
            self.generate_derived_keys(source, peer_public_key, "test")
            if sec.flags & 1:
                self.send(source, port, self.serialize_public_key(self.key_cache[source]["public_key"]), 1, 0)
        elif message_type == 2 and not self.network_key:
            network_key = self.decryption(sec.fc, secdata, sec.mac, source, True)
            self.network_key = network_key
            self.key_cache[source] = {}
        else:
            applayer_data = self.decryption(sec.fc, secdata, sec.mac, source)
        if applayer_data:
            self.receive_callback(source, port, applayer_data)

    def send(self, destination, port, data, message_type = 3, flags = 0):
        framecount = self.new_framecount()
        packet = ZigbearSecurityLayer(flags=flags, message_type=message_type, fc=framecount)
        packet_data = None
        mac = None
        if message_type < 2:
            packet_data = data
        else:
            packet_data, mac = self.encryption(framecount, data.build(), destination, (message_type == 2))
        packet.data = packet_data
        if mac:
            packet.mac = int.from_bytes(mac, 'big')
        self.networkLayer.send(destination, port, packet)

    def generate_public_key(self, source):
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

    # Nonce should be longer (maybe generate a random number)
    def get_nonce(self, framecount, destination):
        return framecount.to_bytes(4, byteorder='big')

    def encryption(self, framecount, data, destination, shared=False):
        key = self.key_cache[destination]["shared_encryption_key"] if shared else self.network_key
        nonce = self.get_nonce(framecount, destination)
        aesgcm = AESGCM(key)
        sk_encrypted = aesgcm.encrypt(nonce, data, None)
        return (sk_encrypted[:-16], sk_encrypted[-16:])

    def decryption(self, framecount, data, mac, source, shared=False):
        key = self.key_cache[source]["shared_encryption_key"] if shared else self.network_key
        nonce = self.get_nonce(framecount, source)
        aesgcm = AESGCM(key)
        return aesgcm.decrypt(nonce, data + mac.to_bytes(16, 'big'), None)
