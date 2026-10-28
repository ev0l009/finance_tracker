from models.types import AccStat, AccDict
from datetime import datetime, timezone
from typing import Any
from utils import validate_amount
from ui import get_category

class Account:
    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        amount: int,
        created_at: datetime | None = None
    ):
        self.id = id
        self.acc_name = acc_name
        self.balance = amount
        self.acc_type = acc_type
        self.acc_status = AccStat.ACTIVE.value
        self.created_at = created_at if created_at else datetime.now(timezone.utc).replace(microsecond=0)

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        instance = cls(
            id = data["id"],
            acc_name = data["acc_name"],
            acc_type = data["acc_type"],
            amount = data["balance"],
            created_at = data["created_at"])
        return instance
    
    def to_dict(self) -> AccDict:
        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "balance": self.balance,
            "acc_type": self.acc_type,
            "acc_status": self.acc_status,
            "created_at": self.created_at.isoformat()
        }

    def show_balance(self):
        print(
            f"Your current balance is {self.balance}."
        )

    def credit(self, amt: int):
        self.balance += amt

    def debit(self, amt: int):
        self.balance -= amt

    def deposit(self):
        print("DEPOSIT")
        amt = input("  Enter amount → ").strip()

        try:
            deposit_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        if deposit_amt == 0:
            print("Null transactions are not permitted")
            return

        self.credit(deposit_amt)
        print(f"Transaction successful. your new balance is {self.balance}")
        return deposit_amt

    def withdraw(self):
        print("WITHDRAWAL")

        amt = input("  Enter amount → ").strip()
        
        try:
            expense_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        if expense_amt == 0:
            print("Null transactions are not permitted")

        if expense_amt > self.balance:
            print("Excessive transactions are not permitted")
            return

        try:
            category = get_category()
        except ValueError as err:
            print(err)
            return

        self.debit(expense_amt)
        print(f"Transaction successful. your new balance is {self.balance}")
        return expense_amt, category

    def deactivate(self):
        print(
            "Account deactivation\n"
            "Warning, deactivating this account means\n"
            "You wont be able to access it and perform transactions with it until it has been activated.\n"
            "1. Proceed\n"
            "2. Return\n"
        )

        choice = input("Select an option to proceed [1,2]: ")

        if choice == "1":
            self.acc_status = AccStat.INACTIVE.value
            print("\nAccount deactivated successfully.\n")
            return

        print("\nOperation cancelled. Returning...\n")