import hashlib
from fastecdsa import keys, curve
from fastecdsa.encoding.pem import PEMEncoder
from base58 import b58encode, b58decode
from utils.crypto import Crypto


# use self-written crypto package
c = Crypto()

# Get address first to generate public key and private key
class Wallet:

    def __init__(self):
        # str
        self.public_key = None
        # int
        self.private_key = None

    # Generate keypair
    def genKeypair(self):
        # Use Elliptic Curve Cryptography to generate private key
        prkey = keys.gen_private_key(curve.P256)
        # Use private key to get public key in the curve -> (x,y)
        pukey = keys.get_public_key(prkey, curve.P256)
        pukey = PEMEncoder.encode_public_key(pukey)
        self.private_key = prkey
        self.public_key = pukey
        return prkey, pukey

    # ripemd160(sha256(public_key)) -> 160 bits unique key
    def hashPubkey(self, pub_key):
        if not isinstance(pub_key, (bytes, bytearray, str)):
            raise TypeError("input should be str or bytes")
        if isinstance(pub_key, (bytes, bytearray, str)):
            pub_key = pub_key.encode("utf-8")
        # sha256
        pub_sha256 = c.sha256(pub_key)
        # ripemd160
        ripemd160_value = c.ripemd160(pub_sha256)
        self.public_key = ripemd160_value
        return ripemd160_value

    def genAddress(self):
        # Generate keypair
        priv_key, pub_key = self.genKeypair()
        # 160 bits hashed public key encode by base58 to generate address
        address = b58encode(self.hashPubkey(pub_key)).decode('utf-8')
        return address
