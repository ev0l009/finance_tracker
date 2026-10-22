from models.types import TrackerData
from ui import get_account_type
import string
import secrets
from models.account import Account

class Tracker:
    def __init__(self):
        self.data: TrackerData = {
            "accounts": {},
            "transactions": []
        }

    def generate_id(self, preffix: str):
        pool = string.ascii_letters + string.digits
        suffix = ''.join(secrets.choice(pool) for _ in range(5))
        return f"{preffix}_{suffix}"

    def create_account(self):
        print("Account Creation\n")

        acc_name = input("Enter Account Name: ")
        if not acc_name.strip():
            print("\nAccount name cannot be empty")
            return 

        if len(acc_name) < 3:
            print("Account name cannot be less than 3 characters\n")
            return

        acc_map = {
            acc["id"]: acc["account_name"]
            for acc in self.data["accounts"].values()
        }

        if acc_name in acc_map.values():
            print("\nAn account with this name already exists.\n")
            return
        
        acc_type = get_account_type()

        if not acc_type:
            return

        print("\nEnter your starting balance or press enter to start with an empty account at 0")
        amt = ("\nEnter your starting balance: ")

        try:
            start_amt = int(amt)
        except ValueError:
            print("\nStarting amount must be an integer.\n")
        
        if start_amt < 0:
            print("\nStarting amount cannot be a negative value.")

        if not amt.strip:
            start_amt = 0
        
        new_acc_id = self.generate_id("acc")

        while new_acc_id in acc_map:
            new_acc_id = self.generate_id("acc")

        new_acc = Account(
            new_acc_id,
            acc_name,
            acc_type,
            amount
        ).to_dict()

        self.data["accounts"][new_acc_id] = new_acc