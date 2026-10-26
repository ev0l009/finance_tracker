from models.types import TrackerData
from ui import get_account_type
import string
import secrets
from models.account import Account
from file_manager.storage import save_tracker_data, load_tracker_data
from utils import validate_acc_name, validate_amount

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
            self.generate_id(self, preffix, field)
        return gen_id

    def create_account(self):
        print("Account Creation\n")

        acc_map: dict[str, str] = {
            acc["id"]: acc["acc_name"]
            for acc in self.data["accounts"].values()
        }

        acc_name = input("Enter Account Name: ")
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

        print("\nEnter your starting balance or press enter to start with an empty account at 0")
        amt = input("\nEnter your starting balance: ")

        try:
            start_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        new_acc_id = self.generate_id("acc", "accounts")

        new_acc = Account(
            new_acc_id,
            acc_name,
            acc_type,
            start_amt
        ).__dict__

        self.data["accounts"][new_acc_id] = new_acc
        print("\nAccount creation successful.\n")

    def save(self):
        save_tracker_data(self.data)

    def load(self):
        self.data = load_tracker_data()