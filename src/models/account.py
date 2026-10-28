from models.types import AccStat, AccDict
from datetime import datetime, timezone
from typing import Any
from utils import validate_amount

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

        self.credit(deposit_amt)
        print(f"Transaction successful. your new balance is {self.balance}")

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

        category = 
#         food — groceries, meals, eating out

# bills — utilities, rent, subscriptions

# transport — fuel, transit, ride-hailing

# airtime — phone credit, data

# health — meds, clinic, insurance

# shopping — clothes, gadgets, personal items

# entertainment — movies, games, streaming

# other — catch-all