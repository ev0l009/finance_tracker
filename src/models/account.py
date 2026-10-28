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
        print("\n  CURRENT BALANCE")
        print("  " + "—" * 25)
        print(f"  Available Funds:  ${self.balance:,.2f}")
        print("  " + "—" * 25 + "\n")

    def credit(self, amt: int):
        self.balance += amt

    def debit(self, amt: int):
        self.balance -= amt

    def deposit(self):
        print("DEPOSIT")
        amt = input("  Enter deposit amount → ").strip()

        try:
            deposit_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        if deposit_amt == 0:
            print("\n  [!] Transaction canceled: Amount must be greater than $0.00.")
            return

        self.credit(deposit_amt)
        print(f"\n  [✓] Transaction successful. New Balance: ${self.balance:,.2f}\n")
        return deposit_amt

    def withdraw(self):
        print("WITHDRAWAL")

        amt = input("  Enter withdrawal amount → ").strip()
        
        try:
            expense_amt = validate_amount(amt)
        except ValueError as err:
            print(err)
            return

        if expense_amt == 0:
            print("\n  [!] Transaction canceled: Amount must be greater than $0.00.")

        if expense_amt > self.balance:
            print("\n  [!] Error: Transaction limit exceeded.")
            return

        try:
            category = get_category()
        except ValueError as err:
            print(err)
            return

        self.debit(expense_amt)
        print(f"\n  [✓] Transaction successful. New Balance: ${self.balance:,.2f}\n")
        return expense_amt, category

    def deactivate(self):
        print("\n  ACCOUNT DEACTIVATION")
        print("  " + "—" * 35)
        print("  ⚠️  Notice: Deactivating this account locks all features")
        print("      and transactions until it is reactivated.")
        print("  1. Proceed with Deactivation")
        print("  2. Cancel and Return\n")

        choice = input("  Select option (1 or 2) → ").strip()

        if choice == "1":
            self.acc_status = AccStat.INACTIVE.value
            print("\n  [✓] Account deactivated successfully.\n")
            return

        print("\n  [i] Operation canceled. Returning...\n")