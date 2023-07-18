from database import AccountDB
from Wallet.wallet import Wallet
from fastecdsa import keys, curve
from base58 import b58decode, b58encode
from fastecdsa.encoding.pem import PEMEncoder


def new_account():
    wallet = Wallet()
    address = wallet.genAddress()
    public_key = wallet.public_key
    private_key = wallet.private_key

    adb = AccountDB()
    adb.insert({'pubkey': public_key, 'address': address})
    return private_key, public_key, address


def get_account():
    adb = AccountDB()
    return adb.find_one()


def recover_account(privatKey):
    orignalpubkey = keys.get_public_key(privatKey, curve.P256)
    orignalpubkey = PEMEncoder.encode_public_key(orignalpubkey)
    pubkey = Wallet().hashPubkey(orignalpubkey)
    address = b58encode(pubkey).decode('utf-8')
    return pubkey, address
