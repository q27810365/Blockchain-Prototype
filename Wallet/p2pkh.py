import hashlib
from fastecdsa import keys, curve, ecdsa
from base58 import b58encode, b58decode
from utils.crypto import Crypto
from Wallet.wallet import Wallet
from fastecdsa.encoding.pem import PEMEncoder
from fastecdsa.encoding.der import DEREncoder
c = Crypto()

class P2pkh:

    # use elliptic curve to generate digital signature using utxo's hash
    # signature will be encoded in DRE format and then base58 encoded
    # will return a pack contains signature and corresponding public key
    def sign(self, utxoHash, prkey) -> dict:
        r, s = ecdsa.sign(utxoHash.encode('utf-8'), prkey, curve.P256)
        signaturepoint = DEREncoder.encode_signature(r, s)
        pukey = keys.get_public_key(prkey, curve.P256)
        pukey = PEMEncoder.encode_public_key(pukey)
        pack = {
            'signature': b58encode(signaturepoint).decode('utf-8'),
            'publickey': pukey,
        }
        return pack

    # first base58 decode the address and compare to the public key
    # second use utxo and the public key to verify the signature
    def verify(self, utxoHash, pack, address) -> bool:
        signature = b58decode(pack['signature'])
        publickey = pack['publickey']
        publickey = Wallet().hashPubkey(publickey)
        try:
            pubkey = b58decode(address).decode('utf-8')
        except ValueError as e:
            print('Wrong Address')
            return False
        if pubkey != publickey:
            print('Hash wrong')
            return False
        orignalSignature = DEREncoder.decode_signature(signature)
        orignalPublicKey = PEMEncoder.decode_public_key(pack['publickey'], curve.P256)
        return ecdsa.verify(orignalSignature, utxoHash.encode('utf-8'), orignalPublicKey, curve.P256)


