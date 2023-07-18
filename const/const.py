# @Written by LI Zijie 2022/11/20 21:30
# Add const veriable SLEEP_TIME and ATTACK_INDEX
#
# from const.const import Const

class Const:
    # BASE_MINETIME
    BASE_MINETIME = 50

    # BASE_DIFFICULTY
    BASE_DIFFICULTY = 1

    # MAX_NONCE
    MAX_NONCE = 2 ** 256

    # Sleep time when simulate double spending attacking
    # Unit : second
    SLEEP_TIME = 20

    # The beginning index for double spending attacking
    ATTACK_INDEX = 5

    # The first time flag of attacking
    FIRST_FLAG = 1

    # MAX_COIN
    MAX_COIN = 21000000

    # REWARD
    REWARD = 20
