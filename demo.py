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
# DEMO 1
# ======================
def demo1():
    wallet1, wallet2, miner, bc = reset_env()

    print("\n=== DEMO 1: Giao dịch hợp lệ ===")

    bc.mine_pending_transactions(wallet1.get_address())

    tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 5)
    tx1.sign_transaction(wallet1)

    bc.add_transaction(tx1)
    bc.mine_pending_transactions(miner.get_address())

    print("Blockchain valid:", bc.is_chain_valid())
    print("Balance wallet1:", bc.get_balance(wallet1.get_address()))


# ======================
# DEMO 2
# ======================
def demo2():
    wallet1, wallet2, miner, bc = reset_env()

    print("\n=== DEMO 2: Sửa dữ liệu (attack) ===")

    bc.mine_pending_transactions(wallet1.get_address())

    tx = Transaction(wallet1.get_address(), wallet2.get_address(), 5)
    tx.sign_transaction(wallet1)

    bc.add_transaction(tx)
    bc.mine_pending_transactions(miner.get_address())

    bc.chain[1].transactions[0].amount = 500

    print("Blockchain valid after attack:", bc.is_chain_valid())


# ======================
# DEMO 3
# ======================
def demo3():
    wallet1, wallet2, miner, bc = reset_env()

    print("\n=== DEMO 3: Chữ ký không hợp lệ ===")

    fake_tx = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    fake_tx.sign_transaction(wallet2)

    try:
        bc.add_transaction(fake_tx)
    except Exception as e:
        print("Rejected transaction:", e)


# ======================
# DEMO 4
# ======================
def demo4():
    wallet1, wallet2, miner, bc = reset_env()

    print("\n=== DEMO 4: Double Spending (chưa fix) ===")

    bc.mine_pending_transactions(wallet1.get_address())

    tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    tx1.sign_transaction(wallet1)

    tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    tx2.sign_transaction(wallet1)

    bc.add_transaction(tx1)
    bc.add_transaction(tx2)

    bc.mine_pending_transactions(miner.get_address())

    print("Blockchain valid:", bc.is_chain_valid())
    print("Balance wallet1:", bc.get_balance(wallet1.get_address()))


# ======================
# DEMO 5
# ======================
def demo5():
    wallet1, wallet2, miner, bc = reset_env()

    print("\n=== DEMO 5: Double Spending (đã fix) ===")

    bc.mine_pending_transactions(wallet1.get_address())

    print("Balance wallet1:", bc.get_balance(wallet1.get_address()))

    tx1 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    tx1.sign_transaction(wallet1)

    tx2 = Transaction(wallet1.get_address(), wallet2.get_address(), 10)
    tx2.sign_transaction(wallet1)

    try:
        bc.add_transaction(tx1)
        bc.add_transaction(tx2)
    except Exception as e:
        print("Rejected transaction:", e)

    bc.mine_pending_transactions(miner.get_address())

    print("Blockchain valid:", bc.is_chain_valid())


# ======================
# DEMO 6
# ======================
def demo6():
    print("\n=== DEMO 6: Data Persistence ===")

    w1, w2, miner, bc = reset_env()

    bc.mine_pending_transactions(w1.get_address())

    tx = Transaction(w1.get_address(), w2.get_address(), 5)
    tx.sign_transaction(w1)

    bc.add_transaction(tx)
    bc.mine_pending_transactions(miner.get_address())

    bc.save_to_file("blockchain_save.json")

    new_bc = Blockchain()
    new_bc.load_from_file("blockchain_save.json")

    print("Số block:", len(new_bc.chain))
    print("Valid:", new_bc.is_chain_valid())
    print("Balance w2:", new_bc.get_balance(w2.get_address()))


# ======================
# MENU (SWITCH CASE)
# ======================
def main():
    demos = {
        "1": demo1,
        "2": demo2,
        "3": demo3,
        "4": demo4,
        "5": demo5,
        "6": demo6,
    }

    while True:
        print("""
========= MENU =========
1. Giao dịch hợp lệ
2. Attack (sửa dữ liệu)
3. Chữ ký sai
4. Double Spending (chưa fix)
5. Double Spending (đã fix)
6. Data Persistence
0. Thoát
========================
""")

        choice = input("Chọn demo: ")

        if choice == "0":
            print("Thoát chương trình...")
            break

        elif choice in demos:
            demos[choice]()
        else:
            print("Lựa chọn không hợp lệ!")

        input("\nNhấn Enter để tiếp tục...")


# ======================
# RUN
# ======================
if __name__ == "__main__":
    main()
