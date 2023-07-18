from utils.crypto import Crypto
import math


class MerkleTree:

    def __init__(self, input):
        if not isinstance(input, list):
            raise TypeError("data must be a str list")

        if not input:
            raise ValueError("Tx is empty")

        self.input = input
        self.nodes = []
        self.root = None

    def new_tree(self):

        input_list = []
        for x in self.input:
            input_list.append(x)

        padfullnum = pow(2, int(math.log(len(input_list), 2)))
        if padfullnum * 2 != len(input_list):
            for x in range(0, padfullnum * 2 - len(input_list)):
                input_list.append('')

        for d in input_list:

            # if isinstance(d, bytes) or isinstance(d, bytearray):
            if isinstance(d, str):

                node = MerkleNode(None, None, d)
                node.new_node()
                self.nodes.append(node)
            else:
                raise TypeError("Wrong data type")

        for i in range(int(math.log(len(input_list), 2))):
            new_level = []

            for j in range(0, len(self.nodes), 2):
                node = MerkleNode(self.nodes[j], self.nodes[j + 1], '')
                node.new_node()
                new_level.append(node)
            self.nodes = new_level

        self.root = self.nodes[0]


class MerkleNode:

    def __init__(self, left, right, input):
        self.Left = left
        self.Right = right

        if isinstance(input, str):
            self.input = input
        else:
            raise TypeError("data is not type str!")

    def new_node(self):
        if not self.Left and not self.Right:
            hash_value = Crypto().sha256(self.input)
            self.input = hash_value
        else:
            prehash = self.Left.input + self.Right.input
            hash_value = Crypto().sha256(prehash)
            self.input = hash_value