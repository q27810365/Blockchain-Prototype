from Database.mongoDB import MongoDB
from utils.crypto import Crypto
from Blocks.merkletree import MerkleTree, MerkleNode
from const.const import Const
from model import Model
from rpc import BroadCast


# @Written by Zhao Zhuoyun 2022/11/17 14:38

class Block(Model):

    # block structure
    def __init__(self, index, timestamp, data, prevHash, difficulty=Const.BASE_DIFFICULTY):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.prevHash = prevHash
        self.difficulty = difficulty
        self.hash = ''
        self.nonce = 0
        self.merkleroot = ''

    # change 1: Adds a new initial property

    # change 2: Added the case where the block is a new block

    # set the difficulty of this block
    def set_difficulty(self):
        # get the previous block's difficulty
        last_block = {}
        for x in MongoDB().getlast('blockchain'):
            last_block = x
            pre_difficulty = x['difficulty']
        # if this block is the first block, set the difficulty with the default value
        if len(last_block) == 0:
            pre_difficulty = Const.BASE_DIFFICULTY
            # using func dynamic_difficulty and previous block's difficulty to compute this block's difficulty
        self.difficulty = self.dynamic_difficulty(pre_difficulty)
        # print("set difficulty")
        MongoDB().close_connect()

    # change 3: Added the case where the block is in the range of the first 10 blocks

    # this func is used to change the difficulty dynamically
    def dynamic_difficulty(self, difficulty):
        # the supposed time of mining one block
        expected_time = Const.BASE_MINETIME
        # get the timestamp of the previous tenth block
        b = MongoDB().getlastn('blockchain', 10)
        timelist = []
        for x in b:
            timelist.append(x['timestamp'])
        MongoDB().close_connect()
        # set the first 10 blocks' difficulty with the default value
        if (len(timelist) < 10):
            return Const.BASE_DIFFICULTY
        timescamp_t1 = timelist[-1]
        # current mined block's timestamp timestamp_t2
        timescamp_t2 = self.timestamp
        # calculate the timestamp gap compared with excepted_time
        actual_time = (timescamp_t2 - timescamp_t1)
        # deviation
        deviation = 1
        # difficulty should be adjusted if:
        # actual_time < factor_a * expected_time，difficulty increase
        factor_a = 0.5
        # actual_time > factor_b * expected_time，difficulty decrease
        factor_b = 2
        if (actual_time < expected_time * factor_a * 10):
            difficulty += deviation
        if (actual_time > expected_time * factor_b * 10):
            difficulty -= deviation
        if difficulty < 0:
            difficulty = 0
        # return adjusted difficulty
        return difficulty

    # compute the hash of the current block
    def get_hash(self):
        header_bin = str(self.index) + str(self.timestamp) + str(self.prevHash) + str(self.difficulty) + str(
            self.nonce) + str(self.data) + str(self.merkleroot)
        self.hash = Crypto().sha256(Crypto().sha256(header_bin))

    # get the merkleroot of the transacions in this block
    def get_merkleroot(self):
        tree = MerkleTree(self.data)
        tree.new_tree()
        self.merkleroot = tree.root.input

    # POW, return the final nonce which satisfy the computing task
    def proof_of_work(self):
        target = 2 ** (256 - self.difficulty)
        # find nonce
        for nonce in range(Const.MAX_NONCE):
            header_bin = str(self.index) + str(self.timestamp) + str(self.prevHash) + str(self.difficulty) + str(
                nonce) + str(self.data) + str(self.merkleroot)
            hash_res = Crypto().sha256(Crypto().sha256(header_bin))

            # check whether index is repeated
            if (self.index_comparison() == 1):
                return -1

            if int(hash_res, 16) < target:
                self.nonce = nonce
                return nonce
        # return -1 if failed to find nonce
        print(f'failed after {Const.MAX_NONCE} tries')
        return -1

    # check whether index is repeated
    # if repeated return 1 otherwise 0
    def index_comparison(self):
        last_block = {}
        list = []
        for x in MongoDB().getlast('blockchain'):
            last_block = x
            list.append(x['index'])
        MongoDB().close_connect()

        if len(last_block) == 0:
            return 0

        last_index = list[-1]
        # compare index
        if (last_index >= self.index):
            return 1
        else:
            return 0

    @staticmethod
    def spread(block):
        BroadCast().new_block(block)

    @classmethod
    def from_dict(cls, bdict):
        b = cls(bdict['index'], bdict['timestamp'], bdict['tx'], bdict['previous_block'])
        b.hash = bdict['hash']
        b.nouce = bdict['nouce']
        return b

    def to_dict(self):
        return self.__dict__