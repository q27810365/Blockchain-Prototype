# coding:utf-8
from account import *
from rpc import get_clients, BroadCast, start_server
from transaction import *
from database import *
import sys
from Blocks.miner import mine, attacker_mine, victim_mine
from node import *
from lib.common import cprint

MODULES = ['account', 'tx', 'blockchain', 'miner', 'node']

def upper_first(string):
    return string[0].upper()+string[1:]

class Node():

    def add(self, args):
        add_node(args[0])
        rpc.BroadCast().add_node(args[0])
        cprint('Allnode',get_nodes())
    
    def run(self, args):
        start_node(args[0])

    def list(self, args):
        for t in RedisDB().getlist('nfl'):
            cprint('Node',t)

class Miner():
    def start(self, args):
        if get_account() == None:
            cprint('ERROR', 'Please create account before start miner.')
            exit()
        start_node(args[0])
        # print("ouput to log")
        while True:
            block = mine().to_dict()
            # with open('log.txt', 'wt') as f:
            cprint('Miner new block', block)

    def attacker(self, args):
        if get_account() == None:
            cprint('ERROR', 'Please create account before start miner.')
            exit()
        start_node(args[0])
        while True:
            block = attacker_mine().to_dict()
            cprint('Attacker new block', block)

    def victim(self, args):
        if get_account() == None:
            cprint('ERROR', 'Please create account before start miner.')
            exit()
        start_node(args[0])
        while True:
            block = victim_mine().to_dict()
            cprint('Victim new block', block)


class Account():
    def create(self, args):
        ac = new_account()
        print("*****Please Write Down Your Private Key******")
        print("****Private Key Will NOT Save On The Disk****")
        cprint('Private Key',ac[0])
        cprint('Public Key',ac[1])
        cprint('Address',ac[2])

    def get(self, args):
        cprint('All Account',AccountDB().read())

    def current(self, args):
        cprint('Current Account', get_account())

class Blockchain():

    def list(self, args):
        for t in MongoDB().getLongestChain():
            cprint('Blockchain', t)
        MongoDB().close_connect()
class Tx():

    def list(self, args):
        for t in MongoDB().getAll('transactions'):
            cprint('Transaction',t)
        MongoDB().close_connect()

    def transfer(self, args):
        tx = Transaction.transfer(args[0], args[1], args[2], int(args[3]))
        tx.pop('_id')
        Transaction.unblock_spread(tx)
        cprint('Transaction transfer', tx)

def usage(class_name):
    module = globals()[upper_first(class_name)]
    print('  ' + class_name + '\r')
    print('    [action]\r')
    for k,v in module.__dict__.items():
        if callable(v):
            print('      %s' % (k,))
    print('\r')

def help():
    print("Usage: python console.py [module] [action]\r")
    print('[module]\n')
    for m in MODULES:
        usage(m)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        help()
        exit()
    module = sys.argv[1]
    if module == 'help':
        help()
        exit()
    if module not in MODULES:
        cprint('Error', 'First arg shoud in %s' % (str(MODULES,)))
        exit()
    mob = globals()[upper_first(module)]()
    method = sys.argv[2]
    # try:
    getattr(mob, method)(sys.argv[3:])
    # except Exception as e:
    #     cprint('ERROR','/(ㄒoㄒ)/~~, Maybe command params get wrong, please check and try again.')