from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.client import ServerProxy
from pymongo.errors import DuplicateKeyError
from node import get_nodes, add_node
from Database.mongoDB import MongoDB
from lib.common import cprint
from utils.crypto import Crypto
from Wallet.p2pkh import P2pkh

server = None

PORT = 8301

p = P2pkh()
class RpcServer():

    def __init__(self, server):
        self.server = server

    def ping(self):
        return True

    def get_blockchain(self) -> list:
        bclist = []
        bcdb = MongoDB()
        # Validation
        for x in bcdb.getAll('blockchain'):
            header_bin = str(x['index']) + str(x['timestamp']) + str(x['prevHash']) +\
                         str(x['difficulty']) + str(x['nonce']) + str(x['data']) + str(x['merkleroot'])
            if x['hash'] == Crypto().sha256(Crypto().sha256(header_bin)):
                bclist.append(x)
        MongoDB().close_connect()
        return bclist

    def new_block(self, block):
        # Validation
        header_bin = str(block['index']) + str(block['timestamp']) + str(block['prevHash']) + \
                    str(block['difficulty']) + str(block['nonce']) + str(block['data']) + str(block['merkleroot'])
        if block['hash'] != Crypto().sha256(Crypto().sha256(header_bin)):
            return False
        try:
            cprint('RPC', block)
            MongoDB().insertOne('blockchain', block)
            cprint('INFO', "Receive new block.")
            MongoDB().close_connect()
            return True
        except DuplicateKeyError:
            print('Existed block, skipped')
            return False



    def get_transactions(self) -> list:
        tdb = MongoDB()
        txs = []
        for x in tdb.getAll("transactions"):
            txs.append(x)
        MongoDB().close_connect()
        return txs

    def new_untransaction(self, untx):
        cprint(__name__, untx)
        '''
            verify(self, utxoHash, pack, address) -> bool
        '''
        txid = untx['hash']
        unLockSig = []
        signature = []
        spublickey = []
        address = []
        # get signature and public key from utxo input
        for x in untx['vin']:
            unLockSig.append(x['unLockSig'])
            signature.append(x['unLockSig']['signature'])
            spublickey.append(x['unLockSig']['publickey'])
        for x in untx['vout']:
            address.append(x['lockSig']['senderAddress'])
        # Normal check
        #  whether it has a signature
        if len(set(signature)) != 1:
            print('Signature is not correct')
            return False
        #  whether it has a public key
        if len(set(spublickey)) != 1:
            print('Signature is not correct')
            return False
        #  whether it has an address
        if len(set(address)) != 1:
            print('Signature is not correct')
            return False
        # use public key and transaction id to verify signature
        if not p.verify(txid, unLockSig[0], address[0]):
            print('Signature is not correct')
            return False
        print('Signature is correct')
        # try to store pending transactions, if they exist, then just skip
        try:
            MongoDB().insertOne('ptransactions', untx)
        except DuplicateKeyError:
            print('Existed pending transactions, skipped')
        cprint('INFO', "Receive new unchecked transaction.")
        MongoDB().close_connect()
        return True

    def blocked_transactions(self, txs):
        try:
            for x in txs:
                MongoDB().insertOne('transactions', x)
            cprint('INFO', "Receive new blocked transactions.")
            MongoDB().close_connect()
            return True
        except DuplicateKeyError:
            print('Existed transactions, skipped')
            return False


    def add_node(self, address):
        add_node(address)
        return True


class RpcClient():
    ALLOW_METHOD = ['get_transactions', 'get_blockchain', 'new_block', 'new_untransaction', 'blocked_transactions',
                    'ping', 'add_node']

    def __init__(self, node):
        self.node = node
        self.client = ServerProxy(node)

    def __getattr__(self, name):
        def noname(*args, **kw):
            if name in self.ALLOW_METHOD:
                return getattr(self.client, name)(*args, **kw)

        return noname


class BroadCast():
    # Calling all functions in RpcServer
    def __getattr__(self, name):
        def processes(*args, **kw):
            nodes = get_clients()
            result = []
            for x in nodes:
                try:
                    result.append(getattr(x, name)(*args, **kw))
                    print(result)
                except ConnectionRefusedError:
                    cprint('WARNNING', 'Failed to connect %s when invoking %s ' % (x.node, name))
                else:
                    cprint('INFOMATION', 'Connect to %s successful invoking %s .' % (x.node, name))
            return result
        return processes


def start_server(ip, port=8301):
    server = SimpleXMLRPCServer((ip, port))
    rpc = RpcServer(server)
    server.register_instance(rpc)
    server.serve_forever()


def get_clients():
    clients = []
    nodes = get_nodes()

    for node in nodes:
        clients.append(RpcClient(node))
    return clients