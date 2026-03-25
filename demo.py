from blockchain import Wallet, Transaction, Blockchain


# ======================
# RESET ENV
# ======================

def reset_env():
    wallet1 = Wallet()
    wallet2 = Wallet()
    miner = Wallet()
    bc = Blockchain()
    return wallet1, wallet2, miner, bc


# ======================
# DEMO 1: Giao dịch hợp lệ
# ======================

wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 1: Giao dịch hợp lệ ===")

tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 5)
tx1.sign_transaction(wallet1)

bc.add_transaction(tx1)
bc.mine_pending_transactions(miner.get_address())

print("Blockchain valid:", bc.is_chain_valid())


# ======================
# DEMO 2: Sửa dữ liệu (attack)
# ======================

print("\n=== DEMO 2: Sửa dữ liệu (attack) ===")

# sửa dữ liệu trong block
bc.chain[1].transactions[0].amount = 500

print("Blockchain valid after attack:", bc.is_chain_valid())


# ======================
# DEMO 3: Chữ ký không hợp lệ
# ======================

wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 3: Chữ ký không hợp lệ ===")

fake_tx = Transaction(wallet1.get_address(), wallet2.get_address(), 10)

# ❌ ký sai (wallet2 ký thay vì wallet1)
fake_tx.sign_transaction(wallet2)

try:
    bc.add_transaction(fake_tx)
except Exception as e:
    print("Rejected transaction:", e)


# ======================
# DEMO 4: Double Spending (chưa fix)
# ======================

wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 4: Double Spending (chưa fix) ===")

tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx1.sign_transaction(wallet1)

tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx2.sign_transaction(wallet1)

bc.add_transaction(tx1)
bc.add_transaction(tx2)  # ❗ cùng tiền nhưng gửi 2 lần

bc.mine_pending_transactions(miner.get_address())

print("Blockchain valid:", bc.is_chain_valid())


# ======================
# DEMO 5: Double Spending (đã fix)
# ======================

wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 5: Double Spending (đã fix) ===")

# đào 1 block để wallet1 có tiền
bc.mine_pending_transactions(wallet1.get_address())

print("Balance wallet1:", bc.get_balance(wallet1.get_address()))

tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx1.sign_transaction(wallet1)

tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx2.sign_transaction(wallet1)

try:
    bc.add_transaction(tx1)
    bc.add_transaction(tx2)  # ❌ sẽ bị chặn nếu đã fix balance
except Exception as e:
    print("Rejected transaction:", e)

bc.mine_pending_transactions(miner.get_address())

print("Blockchain valid:", bc.is_chain_valid())