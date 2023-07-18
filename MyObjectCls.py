from PyQt5.QtCore import *
from account import *
from transaction import *
from database import *
from Blocks.miner import mine
from node import *
from lib.common import cprint
from Database.mongoDB import MongoDB


class MyObjectCls(QObject):
    sigSetParentWindowTitle = pyqtSignal(str)
    
    def __init__(self, parent=None):
        QObject.__init__(self, parent)
            
    @pyqtSlot(str)
    def createAccount(self):
        ac = new_account()
        print("*****Please Write Down Your Private Key******")
        print("****Private Key Will NOT Save On The Disk****")
        cprint('Private Key', ac[0])
        cprint('Public Key', ac[1])
        cprint('Address', ac[2])

    @pyqtSlot(str)
    def getAllAccount(self):
        cprint('All Account',AccountDB().read())

    @pyqtSlot(str)
    def currentAccount(self):
        cprint('Current Account', get_account())

    @pyqtSlot(str)
    def startMinning(self, args):
        if get_account() == None:
            cprint('ERROR', 'Please create account before start miner.')
            exit()
        start_node(args)
        while True:
            block = mine().to_dict()
            cprint('Miner new block', block)

    @pyqtSlot(str)
    def addToBlockchain(self, args):
        add_node(args)
        rpc.BroadCast().add_node(args)
        cprint('Allnode', get_nodes())

    @pyqtSlot(str)
    def run(self, args):
        start_node(args)

    @pyqtSlot(str)
    def listAllNodes(self, args):
        for t in RedisDB().getlist('nfl'):
            cprint('Node', t)

    @pyqtSlot(str)
    def listBlockchain(self, args):
        for t in MongoDB().getLongestChain():
            cprint('Blockchain', t)
        MongoDB().close_connect()

    @pyqtSlot(str, str, str, str)
    def sendTransaction(self, address1, address2, amount, psk):
        tx = Transaction.transfer(address1, address2, amount, int(psk))
        tx.pop('_id')
        Transaction.unblock_spread(tx)
        cprint('Transaction transfer', tx)

    @pyqtSlot(str)
    def showTranList(self):
        for t in MongoDB().getAll('transactions'):
            cprint('Transaction', t)
        MongoDB().close_connect()

