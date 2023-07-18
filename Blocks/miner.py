from Blocks.block import Block
import time
from const.const import Const
from transaction import Vout, Transaction
from account import get_account
from Database.mongoDB import MongoDB
from Database.redisDB import RedisDB



# @Written by LI Zijie 2022/11/15 14:28
# task1: miner挖新块，跟已经改好的代码对上 √
# task2: 初始hash要修改方法赋值不对。 make = hash [header + nonce] √

def reward():
    reward = Vout(get_account()['address'], Const.REWARD, {'senderAddress': get_account()['address']})
    tx = Transaction([], reward)
    return tx


# genesis coinbase
def coinbase():
    # genesis reward
    miner_reward = reward()
    # genesis block
    coinbase_block = Block(0, int(time.time()), [miner_reward.hash], "")

    # calculate difficulty
    coinbase_block.set_difficulty()
    coinbase_block.get_merkleroot()

    # pow
    coinbase_block.proof_of_work()

    # calculate hash
    coinbase_block.get_hash()

    # Save block and transactions to database.
    MongoDB().insertOne('blockchain', coinbase_block.to_dict())
    MongoDB().insertOne('transactions', miner_reward.to_dict())
    MongoDB().close_connect()

    return coinbase_block


# mining function
def mine():
    # prevent mining repeated block
    loop_flag = -1
    while (loop_flag == -1):
        """
        Main miner method.
        """
        # Found last block and unchecked transactions.
        last_block = {}
        data = {
            "currentHeight": 1
        }
        for x in MongoDB().getlast('blockchain'):
            last_block = x
        if last_block == {}:
            last_block = coinbase()
            RedisDB().set("bch", data)
        else:
            data["currentHeight"] = last_block["index"]
            RedisDB().set("bch", data)
        untxdb = MongoDB()
        # Miner reward
        miner_reward = reward()

        untx_hashes = []
        untxs = []
        for x in untxdb.getAll('ptransactions'):
            untxs.append(x)
        if untxs is not None:
            # Clear the untransaction database if successfully mine
            untxdb.delete('ptransactions', {})
        for x in untxs:
            untx_hashes.append(x['hash'])

        untxs.append(miner_reward.to_dict())

        # Miner reward is the first transaction.
        untx_hashes.insert(0, miner_reward.hash)
        new_block = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
        new_block.set_difficulty()
        new_block.get_merkleroot()
        loop_flag = new_block.proof_of_work()



    untxdb.close_connect()
    new_block.get_hash()
    # Save block and transactions to database.
    # MongoDB
    MongoDB().insertOne('blockchain', new_block.to_dict())
    # insert unpacked transactions(coinbase + transfer)
    for x in untxs:
        MongoDB().insertOne('transactions', x)
        x.pop('_id')
    # Broadcast to other nodes
    cbdict = new_block.to_dict()
    cbdict.pop('_id')
    Block.spread(cbdict)
    Transaction.blocked_spread(untxs)

    MongoDB().close_connect()
    return new_block

# attacker mine function
def attacker_mine():
    loop_flag = -1
    while (loop_flag == -1):
        """
        Main miner method.
        """
        # Found last block and unchecked transactions.
        data = {
            "currentHeight": 1
        }
        last_block = {}
        for x in MongoDB().getlast('blockchain'):
            last_block = x
        if last_block == {}:
            last_block = coinbase()
            # Note codes in next line when test
            RedisDB().set("bch", data)
        else:
            if Const.FIRST_FLAG == 1:
                """Attacker sets the ordered index"""
                last_attack_index_block = []
                for x in MongoDB().getlastn('blockchain', Const.ATTACK_INDEX):
                    last_attack_index_block.append(x)
                data['currentHeight'] = last_attack_index_block[-1]['index']
            else:
                data['currentHeight'] = last_block['index']

            # Test: print the currentHeight
            print("CurrentHeight =" + (str)(data['currentHeight']))
            # Note codes in next line when test
            RedisDB().set("bch", data)

        untxdb = MongoDB()
        # Miner reward
        miner_reward = reward()
        untx_hashes = []
        untxs = []
        for x in untxdb.getAll('ptransactions'):
            untxs.append(x)
        if untxs is not None:
            # Clear the untransaction database if successfully mine
            untxdb.delete('ptransactions', {})
        for x in untxs:
            untx_hashes.append(x['hash'])

        untxs.append(miner_reward.to_dict())

        # Miner reward is the first transaction.
        untx_hashes.insert(0, miner_reward.hash)

        # create new block
        if Const.FIRST_FLAG == 1:
            new_block = Block(last_attack_index_block[-1]['index'] + 1, int(time.time()), untx_hashes, last_attack_index_block[-1]['hash'])
        else:
            new_block = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
        # setup pre_difficulty和difficulty
        new_block.set_difficulty()
        new_block.get_merkleroot()
        # calculate nonce
        loop_flag = new_block.proof_of_work()

    Const.FIRST_FLAG = 0
    # Attacker doesn't sleep
    untxdb.close_connect()
    # calculate new block's hash
    new_block.get_hash()
    # Save block and transactions to database.
    MongoDB().insertOne('blockchain', new_block.to_dict())
    for x in untxs:
        MongoDB().insertOne('transactions', x)
        x.pop('_id')
    # Broadcast to other nodes
    cbdict = new_block.to_dict()
    cbdict.pop('_id')
    Block.spread(cbdict)
    Transaction.blocked_spread(untxs)

    MongoDB().close_connect()
    return new_block

# victim mine function includes time.sleep()
def victim_mine():
    loop_flag = -1
    while (loop_flag == -1):
        """
        Main miner method.
        """
        # Found last block and unchecked transactions.
        last_block = {}
        data = {
            "currentHeight": 1
        }
        for x in MongoDB().getlast('blockchain'):
            last_block = x
        if last_block == {}:
            last_block = coinbase()
            # Note codes in next line when test
            RedisDB().set("bch", data)
        else:
            data["currentHeight"] = last_block["index"]
            # Note codes in next line when test
            RedisDB().set("bch", data)
        untxdb = MongoDB()
        # Miner reward
        miner_reward = reward()
        untx_hashes = []
        untxs = []
        for x in untxdb.getAll('ptransactions'):
            untxs.append(x)
        if untxs is not None:
            # Clear the untransaction database if successfully mine
            untxdb.delete('ptransactions', {})
        for x in untxs:
            untx_hashes.append(x['hash'])

        untxs.append(miner_reward.to_dict())

        # Miner reward is the first transaction.
        untx_hashes.insert(0, miner_reward.hash)
        new_block = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
        new_block.set_difficulty()
        new_block.get_merkleroot()
        # Simulate double spending attack
        time.sleep(100)
        loop_flag = new_block.proof_of_work()

    untxdb.close_connect()
    new_block.get_hash()
    # Save block and transactions to database.
    MongoDB().insertOne('blockchain', new_block.to_dict())

    for x in untxs:
        MongoDB().insertOne('transactions', x)
        x.pop('_id')
    # Broadcast to other nodes
    cbdict = new_block.to_dict()
    cbdict.pop('_id')
    Block.spread(cbdict)
    Transaction.blocked_spread(untxs)

    MongoDB().close_connect()
    return new_block


def mineds(atindex):
    last_block = {}
    loop_flag = -1
    while (loop_flag == -1):

        data = {
            "currentHeight": 1
        }
        for x in MongoDB().get('blockchain', {'index': atindex}):
            last_block = x
        if last_block == {}:
            last_block = coinbase()
            RedisDB().set("bch", data)
        else:
            data["currentHeight"] = last_block["index"]
            RedisDB().set("bch", data)
        untxdb = MongoDB()
        # Miner reward
        miner_reward = reward()
        untx_hashes = []
        untxs = []
        for x in untxdb.getAll('ptransactions'):
            untxs.append(x)
        if untxs is not None:
            # Clear the untransaction database if successfully mine
            untxdb.delete('ptransactions', {})
        for x in untxs:
            untx_hashes.append(x['hash'])

        untxs.append(miner_reward.to_dict())

        # Miner reward is the first transaction.
        untx_hashes.insert(0, miner_reward.hash)

        new_block = Block(last_block['index'] + 1, int(time.time()), untx_hashes, last_block['hash'])
        new_block.set_difficulty()
        new_block.get_merkleroot()
        loop_flag = new_block.proof_of_work()

        atindex += 1

    untxdb.close_connect()
    new_block.get_hash()
    # Save block and transactions to database.

    MongoDB().insertOne('blockchain', new_block.to_dict())

    for x in untxs:
        MongoDB().insertOne('transactions', x)
        x.pop('_id')
    # Broadcast to other nodes

    cbdict = new_block.to_dict()
    cbdict.pop('_id')
    Block.spread(cbdict)

    Transaction.blocked_spread(untxs)

    MongoDB().close_connect()
    return new_block