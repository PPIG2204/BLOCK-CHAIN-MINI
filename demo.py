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
# DEMO 1: Giao dịch hợp lệ (đã fix)
# ======================
wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 1: Giao dịch hợp lệ ===")

# HOTFIX: Đào 1 block cho wallet1 để wallet1 có tiền (reward mặc định là 10)
bc.mine_pending_transactions(wallet1.get_address()) 

# Bây giờ wallet1 đã có 10, có thể gửi 5 cho wallet2
tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 5)
tx1.sign_transaction(wallet1)

bc.add_transaction(tx1)
bc.mine_pending_transactions(miner.get_address())

print("Blockchain valid:", bc.is_chain_valid())
print("Balance wallet1:", bc.get_balance(wallet1.get_address()))

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
# DEMO 4: Double Spending (đã fix)
# ======================
wallet1, wallet2, miner, bc = reset_env()

print("\n=== DEMO 4: Double Spending (chưa fix) ===")

# HOTFIX: Đào 1 block để wallet1 có tiền (10 coins)
bc.mine_pending_transactions(wallet1.get_address())

tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx1.sign_transaction(wallet1)

tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
tx2.sign_transaction(wallet1)

bc.add_transaction(tx1)
bc.add_transaction(tx2)  # Trong DEMO 4, logic này sẽ lỗi nếu ví không đủ 20

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

# ======================
# DEMO 6: Data Persistence
# ======================
print("\n=== DEMO 6: Data Persistence ===")

# 1. Setup và tạo dữ liệu
w1, w2, miner, bc_persist = reset_env()
bc_persist.mine_pending_transactions(w1.get_address()) # w1 nhận 10 coins

tx = Transaction(w1.get_address(), w2.get_address(), 5)
tx.sign_transaction(w1)
bc_persist.add_transaction(tx)
bc_persist.mine_pending_transactions(miner.get_address())

# 2. Lưu vào file
bc_persist.save_to_file("blockchain_save.json")

# 3. Tạo instance mới và tải lại
new_bc = Blockchain()
new_bc.load_from_file("blockchain_save.json")

print("Dữ liệu đã tải thành công?")
print("- Số khối trong chain:", len(new_bc.chain))
print("- Blockchain hợp lệ:", new_bc.is_chain_valid())
print("- Số dư w2 (phải là 5):", new_bc.get_balance(w2.get_address()))
