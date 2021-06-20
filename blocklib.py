from time import time

import json
import hashlib


class Blockchain(object):

    def __init__(self):
        self.chain = []
        self.file = []

        # the genesis (very first) block in the chain
        self.new_block(previous_hash='1', proof=2)

    def __len__(self):
        return len(self.chain)

    def __getitem__(self, item):
        return self.chain[item]

    def __setitem__(self, key, value):
        self.chain[key] = value

    @property
    def last_block(self) -> dict:
        return self.chain[-1]

    @classmethod
    def fromchain(cls, other_chain: list):
        """
        Resets the blockchain completely by passing it another chain

        :param other_chain: <list> The chain the new blockchain is supposed to have
        :return: <Blockchain>
        """
        new_blockchain = Blockchain()
        new_blockchain.chain = other_chain
        return new_blockchain

    def new_block(self, proof: int, previous_hash=None) -> dict:
        """
        Create a new block in the blockchain which holds a slice of data

        :param proof: <int> The proof given by the proof of work algorithm
        :param previous_hash: (optional) <str> Hash of the previous block
        :return: <dict> New block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'file': self.file,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }

        # reset the current file slice
        self.file = []
        self.chain.append(block)
        return block

    def new_transaction(self, values: dict) -> int:
        """
        Creates a new transaction to go into the next mined Block

        :param values: <dict> Dictionary containing listed parameters:

        - author_id: Node ID of the sender
        - file: The hash of the file being sent. This way, the file doesn't need to be stored in the block but it still can not be altered
        - recipient_node: Node ID of the recipient
        - path: The path where the file will get stored (adding it to the blockchain disallows the owner to move the file)
        - transaction_id:  ID of the transaction
        :return: <int> The index of the block that will hold this transaction
        """

        self.file.append(values)

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof: int) -> int:
        """
        Simple proof of work algorithm:
         - find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'
         - p is the previous proof, and p' is the new proof

        :param last_proof: <int>
        :return: <int>
        """

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    def valid_chain(self) -> bool:
        """
        Determine if a given blockchain is valid

        :return: <bool> True if valid, False if not
        """

        last_block = self.chain[0]
        current_index = 1

        while current_index < len(self.chain):
            block = self.chain[current_index]
            # check that the hash of the block is correct

            if block['previous_hash'] != self.hash(last_block):
                return False

            # check that the proof of work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1

        return True

    def mine(self, miner: str = None) -> tuple:
        """
        Validates another block.

        :param miner: (Optional) <str> The miner that mined the new block
        :return: <tuple> A tuple of <bool> and either the new block or 0 if it didn't work
        """

        last_block = self.last_block
        proof = self.proof_of_work(last_block['proof'])
        # add the new block to the chain if the proof is true
        if self.valid_proof(last_block['proof'], proof):

            prev_hash = self.hash(last_block)
            block = self.new_block(proof, prev_hash)
            if miner:
                self.new_transaction({'This block has been proudly mined by': miner})
            return True, block

        else:
            return False, 0

    def full_chain(self) -> dict:
        """
        :return: <dict> The complete blockchain chain and its length
        """
        return {
            'chain': self.chain,
            'length': len(self)
        }

    @staticmethod
    def hash(block: dict) -> str:
        """
        Creates a SHA-256 hash of a block

        :param block: <dict> Block
        :return: <str> The hash string of the block
        """

        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        Validates the proof: does hash(last_proof, proof) contain 4 trailing zeroes?

        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: <bool> True if correct, False if not
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == '0000'
