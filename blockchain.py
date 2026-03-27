import hashlib
import json
import time
from ecdsa import SigningKey, VerifyingKey, SECP256k1


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

        if not self.signature:
            return False

        try:
            vk = VerifyingKey.from_string(
                bytes.fromhex(self.sender),
                curve=SECP256k1
            )

            message = json.dumps(self.to_dict(), sort_keys=True)

            return vk.verify(
                bytes.fromhex(self.signature),
                message.encode()
            )

        except:
            return False


# ======================
# BLOCK
# ======================

class Block:

    def __init__(self, index, transactions, previous_hash):

        self.index = index
        self.timestamp = time.time()

        # ⚠️ copy list để tránh bị sửa ngoài
        self.transactions = transactions.copy()

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

    # ======================
    # BALANCE (FIX DOUBLE SPEND)
    # ======================
    def get_balance(self, address):
        balance = 0

        for block in self.chain:
            for tx in block.transactions:
                if tx.sender == address:
                    balance -= tx.amount
                if tx.receiver == address:
                    balance += tx.amount

        return balance

    # ======================
    # ADD TRANSACTION
    # ======================
    def add_transaction(self, transaction):

        if not transaction.is_valid():
            raise Exception("Invalid transaction")

        if transaction.sender != "SYSTEM":
            if self.get_balance(transaction.sender) < transaction.amount:
                raise Exception("Not enough balance")

        self.pending_transactions.append(transaction)

    # ======================
    # MINING
    # ======================
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

    # ======================
    # VALIDATION (UPGRADE)
    # ======================
    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current = self.chain[i]
            previous = self.chain[i - 1]

            # check hash
            if current.hash != current.calculate_hash():
                return False

            # check link
            if current.previous_hash != previous.hash:
                return False

            # 🔥 check transaction inside block
            for tx in current.transactions:
                if not tx.is_valid():
                    return False

        return True
    # ======================
    # DATA PERSISTENCE
    # ======================
    def save_to_file(self, filename="blockchain_data.json"):
            import json
            chain_data = []
            for block in self.chain:
                block_dict = {
                    "index": block.index,
                    "timestamp": block.timestamp,
                    "transactions": [
                        {
                            "sender": t.sender,
                            "receiver": t.receiver,
                            "amount": t.amount,
                            "signature": t.signature
                        } for t in block.transactions
                    ],
                    "previous_hash": block.previous_hash,
                    "nonce": block.nonce,
                    "hash": block.hash
                }
                chain_data.append(block_dict)
            with open(filename, "w") as f:
                json.dump(chain_data, f, indent=4)
            print(f"--- Saved blockchain to {filename} ---")

    def load_from_file(self, filename="blockchain_data.json"):
        import json
        import os
        if not os.path.exists(filename):
            print("No save file found.")
            return
        with open(filename, "r") as f:
            chain_data = json.load(f)
        self.chain = []
        for block_dict in chain_data:
            transactions = [Transaction(tx["sender"], tx["receiver"], tx["amount"], tx.get("signature")) 
                            for tx in block_dict["transactions"]]
            block = Block(block_dict["index"], transactions, block_dict["previous_hash"])
            block.timestamp = block_dict["timestamp"]
            block.nonce = block_dict["nonce"]
            block.hash = block_dict["hash"]
            self.chain.append(block)
        print(f"--- Loaded blockchain from {filename} ---")
