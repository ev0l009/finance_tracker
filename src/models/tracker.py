from models.types import TrackerData
from ui import get_account_type, select_acc
import string
import secrets
from models.account import Account
from file_manager.storage import save_tracker_data, load_tracker_data
from utils import validate_acc_name, validate_amount
from models.types import AccDict, AccStat

class Tracker:
    def __init__(self):
        self.data: TrackerData = {
            "accounts": {},
            "transactions": []
        }

    def generate_id(self, preffix: str, field: str):
        pool = string.ascii_letters + string.digits
        suffix = ''.join(secrets.choice(pool) for _ in range(5))
        gen_id = f"{preffix}_{suffix}"
        while gen_id in self.data[field]:
            self.generate_id(preffix, field)
        return gen_id

    def create_account(self):
        print("\n  ACCOUNT CREATION")
        print("  " + "—" * 20)

        acc_map = {
            acc["id"]: acc["acc_name"]
            for acc in self.data["accounts"].values()
        }

        acc_name = input("  Enter account name → ").strip()
        try:
            valid_acc_name = validate_acc_name(acc_name, acc_map)
        except ValueError as err:
            print(err)
            return
        
        try:
            acc_type = get_account_type()
        except ValueError as err:
            print(err)
            return

        print("\n  [i] Press Enter to start with an empty balance ($0.00).")
        amt = input("  Enter starting balance → ").strip()

        try:
            start_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        new_acc_id = self.generate_id("acc", "accounts")

        new_acc: AccDict = Account(
            new_acc_id,
            valid_acc_name,
            acc_type,
            start_amt
        ).to_dict()

        self.data["accounts"][new_acc_id] = new_acc
        print("\n  [✓] Account creation successful.\n")

    def list_accounts(self):
        print("\n  ACTIVE ACCOUNTS")
        print("  " + "—" * 58)
        
        active_accounts = [
            acc
            for acc in self.data["accounts"].values()
            if acc["acc_status"] == AccStat.ACTIVE.value
        ]
        
        if not active_accounts:
            print("  [i] There are no active accounts right now.\n")
            return

        print(f"  {'Account Name':<16} {'Account ID':<12} {'Type':<12} {'Balance':>12}")
        print("  " + "—" * 58)
        
        for acc in active_accounts:
            name_trunc = acc['acc_name'].title()[:14] + ".." if len(acc['acc_name']) > 14 else acc['acc_name'].title()
            type_str = acc['acc_type'].capitalize()
            balance_str = f"${acc['balance']:,.2f}"
            
            print(f"  {name_trunc:<16} {acc['id']:<12} {type_str:<12} {balance_str:>12}")
            
        print("  " + "—" * 58 + "\n")

    def transfer(self):
        print("\n  FUND TRANSFER")
        print("  " + "—" * 20)

        if len(self.data["accounts"]) < 2:
            print("  [!] Action unavailable: You need at least 2 active accounts to make a transfer.\n")
            return

        acc_map = {
            acc["id"]: acc["acc_name"]
            for acc in self.data["accounts"].values()
            if acc["acc_status"] == AccStat.ACTIVE.value
        }

        try:
            sender_acc_id = select_acc(
                acc_map,
                "Source Account"
            )
        except ValueError as err:
            print(err)
            return

        sender_acc = self.data["accounts"][sender_acc_id]

        amt = input("  Enter transfer amount → ").strip()

        try:
            transfer_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        if transfer_amt > sender_acc["balance"]:
            print("\n  [!] Error: Limit exceeded. Excessive transfers are not allowed.\n")
            return

        try:
            reciever_acc_id = select_acc(
                acc_map, 
                sender_acc_id,
                "Target Account"
            )
        except ValueError as err:
            print(err)
            return

        receiver_acc = self.data["accounts"][reciever_acc_id]

        sender_acc["balance"] -= transfer_amt
        receiver_acc["balance"] += transfer_amt

        

        print("\n  [✓] Transfer completed successfully.\n")


    def save(self):
        save_tracker_data(self.data)

    def load(self):
        self.data = load_tracker_data()