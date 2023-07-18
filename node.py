import multiprocessing
import rpc
from Database.mongoDB import MongoDB
from Database.redisDB import RedisDB
from lib.common import cprint

def start_node(hostport='0.0.0.0:3009'):
    init_node()
    cprint('INFO', 'Node initialize success.')
    try:
        if hostport.find('.') != -1:
            host,port = hostport.split(':')
        else:
            host = '0.0.0.0'
            port = hostport
    except Exception:
        cprint('ERROR','params must be {port} or {host}:{port} , ps: 3009 or 0.0.0.0:3009')
    p = multiprocessing.Process(target=rpc.start_server,args=(host,int(port)))
    p.start()
    cprint('INFO','Node start success. Listen at %s.' % (hostport,))

def init_node():
    """
    Download blockchain from node compare with local database and select the longest blockchain.
    """
    all_node_blockchains = rpc.BroadCast().get_blockchain()
    all_node_txs = rpc.BroadCast().get_transactions()
    bcdb = MongoDB()
    txdb = MongoDB()
    blockchain, transactions = [], []
    for x in bcdb.getAll('blockchain'):
        blockchain.append(x)
    for x in txdb.getAll('transactions'):
        transactions.append(x)
    # all_node_blockchains:[[bc1],[bc2],[bc3]....]
    for bc in all_node_blockchains:
        if len(bc) > len(blockchain):
            bcdb.delete('blockchain', {})
            for x in bc:
                bcdb.insertOne('blockchain', x)

    for txs in all_node_txs:
        if len(txs) > len(transactions):
            txdb.delete('transactions', {})
            for x in txs:
                txdb.insertOne('transactions', x)
    bcdb.close_connect()
    txdb.close_connect()
    
def get_nodes():
    return RedisDB().getlist('nfl')



def add_node(address):
    ndb = RedisDB()
    all_nodes = ndb.getlist('nfl')
    if address.find('http') != 0:
        address = 'http://' + address
    all_nodes.append(address)
    ndb.remove('nfl')
    for x in rm_dup(all_nodes):
        ndb.setlist('nfl', x)
    return address

def check_node(address):
    pass

def rm_dup(nodes):
    return sorted(set(nodes)) 
    
if __name__=='__main__':
    start_node(3009)