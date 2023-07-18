import time
import hashlib
from model import Model
from rpc import BroadCast
from Database.mongoDB import MongoDB
from Wallet.p2pkh import P2pkh
from Wallet.wallet import Wallet

pay = P2pkh()
w = Wallet()

class Vin(Model):
    def __init__(self, utxo_hash, amount, unLockSig={}):
        self.hash = utxo_hash
        self.amount = amount
        self.unLockSig = unLockSig


class Vout(Model):
    def __init__(self, receiver, amount, lockSig={}):
        self.receiver = receiver
        self.amount = amount
        self.hash = hashlib.sha256(
            (str(time.time()) + str(self.receiver) + str(self.amount)).encode('utf-8')).hexdigest()
        self.lockSig = lockSig

    @classmethod
    def get_unspent(cls, addr):
        unspent = []
        all_tx = []
        for x in MongoDB().getAll('transactions'):
            all_tx.append(x)
        print(all_tx[0])

        spend_vin = []
        [spend_vin.extend(item['vin']) for item in all_tx]
        has_spend_hash = [vin['hash'] for vin in spend_vin]
        for item in all_tx:
            # Vout receiver is addr and the vout hasn't spent yet.
            for vout in item['vout']:
                if vout['receiver'] == addr and vout['hash'] not in has_spend_hash:
                    unspent.append(vout)
        return [Vin(tx['hash'], tx['amount']) for tx in unspent]


class Transaction:
    def __init__(self, vin, vout):
        self.timestamp = int(time.time())
        self.vin = vin
        self.vout = vout
        self.hash = self.gen_hash()

    def gen_hash(self):
        return hashlib.sha256((str(self.timestamp) + str(self.vin) + str(self.vout)).encode('utf-8')).hexdigest()

    @classmethod
    def transfer(cls, from_addr, to_addr, amount, prikey):

        if not isinstance(amount, int):
            amount = int(amount)
        unspents = Vout.get_unspent(from_addr)
        ready_utxo, change = generateOutputs(unspents, amount)
        print('ready_utxo', ready_utxo[0].to_dict())
        vin = ready_utxo
        vout = []
        vout.append(Vout(to_addr, amount))
        vout.append(Vout(from_addr, change))
        tx = cls(vin, vout)
        # Digtal Signature
        for x in tx.vin:
            x.unLockSig = pay.sign(tx.hash, prikey)
        for x in vout:
            x.lockSig = {'senderAddress': from_addr}
        tx_dict = tx.to_dict()
        MongoDB().insertOne('ptransactions', tx_dict)
        MongoDB().close_connect()
        return tx_dict

    @staticmethod
    def unblock_spread(untx):
        BroadCast().new_untransaction(untx)

    @staticmethod
    def blocked_spread(txs):
        BroadCast().blocked_transactions(txs)

    def to_dict(self):
        dt = self.__dict__
        if not isinstance(self.vin, list):
            self.vin = [self.vin]
        if not isinstance(self.vout, list):
            self.vout = [self.vout]
        dt['vin'] = [i.__dict__ for i in self.vin]
        dt['vout'] = [i.__dict__ for i in self.vout]
        return dt


def generateOutputs(unspent, min_value):
    if not unspent:
        return None
    # divided into two list
    lessers = [utxo for utxo in unspent if utxo.amount < min_value]
    greaters = [utxo for utxo in unspent if utxo.amount >= min_value]
    key_func = lambda utxo: utxo.amount
    greaters.sort(key=key_func)
    if greaters:
        # find greater in lessers
        min_greater = greaters[0]
        change = min_greater.amount - min_value
        return [min_greater], change
    # sort to find the smallest utxo
    lessers.sort(key=key_func, reverse=True)
    result = []
    accum = 0
    for utxo in lessers:
        result.append(utxo)
        accum += utxo.amount
        if accum >= min_value:
            change = accum - min_value
            return result, change
    return None, 0
