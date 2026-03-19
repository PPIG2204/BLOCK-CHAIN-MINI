import hashlib
import json
import time
from ecdsa import SigningKey, SECP256k1


# ======================
# WALLET
# ======================

class Wallet:

    def __init__(self):
        self.private_key = SigningKey.generate(curve=SECP256k1)
        self.public_key = self.private_key.get_verifying_key()

    def get_address(self):
        return self.public_key.to_string().hex()

    def sign(self, message):
        return self.private_key.sign(message.encode()).hex()


# ======================
# TRANSACTION
# ======================

class Transaction:

    def __init__(self, sender, receiver, amount, signature=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.signature = signature

    def to_dict(self):
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount
        }

    def sign_transaction(self, wallet):
        message = json.dumps(self.to_dict(), sort_keys=True)
        self.signature = wallet.sign(message)

    def is_valid(self):

        if self.sender == "SYSTEM":
            return True

        try:
            from ecdsa import VerifyingKey

            vk = VerifyingKey.from_string(bytes.fromhex(self.sender), curve=SECP256k1)

            message = json.dumps(self.to_dict(), sort_keys=True)

            return vk.verify(bytes.fromhex(self.signature), message.encode())

        except:
            return False


# ======================
# BLOCK
# ======================

class Block:

    def __init__(self, index, transactions, previous_hash):

        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):

        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [t.to_dict() for t in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)

        return hashlib.sha256(block_string.encode()).hexdigest()


# ======================
# BLOCKCHAIN
# ======================

class Blockchain:

    difficulty = 4

    def __init__(self):

        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):

        return Block(0, [], "0")

    def get_latest_block(self):

        return self.chain[-1]

    def add_transaction(self, transaction):

        if not transaction.is_valid():
            raise Exception("Invalid transaction")

        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self, miner_address):

        reward_tx = Transaction("SYSTEM", miner_address, 10)
        self.pending_transactions.append(reward_tx)

        block = Block(
            len(self.chain),
            self.pending_transactions,
            self.get_latest_block().hash
        )

        self.mine_block(block)

        self.chain.append(block)

        self.pending_transactions = []

    def mine_block(self, block):

        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()

        print("Block mined:", block.hash)

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.calculate_hash():
                return False

            if current.previous_hash != previous.hash:
                return False

        return True


# ======================
# DEMO
# ======================

wallet1 = Wallet()
wallet2 = Wallet()
miner = Wallet()

bc = Blockchain()

tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 5)
tx1.sign_transaction(wallet1)

bc.add_transaction(tx1)

bc.mine_pending_transactions(miner.get_address())

print("Blockchain valid:", bc.is_chain_valid())

# thử sửa dữ liệu

bc.chain[1].transactions[0].amount = 500

print("Blockchain valid after attack:", bc.is_chain_valid())