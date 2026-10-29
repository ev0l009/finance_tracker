"""Initializes account objects and performs account specific actions."""

from models.types import AccStat, AccType, AccDict, AccDashState
from datetime import datetime, timezone
from typing import Any
from utils import validate_amount
from ui import get_category
from exceptions import InvalidAmountError, InvalidOptionError

class Account:
    """Initializes an account object with structural, type-validated, and write-once invariants."""
    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        amount: int,
        created_at: datetime | None = None
    ):
        # Set immutable properties using internal underscored variables
        if not id or not id.strip():
            raise ValueError("Account ID cannot be empty.")
        self._id = id

        # Strict Enum validation for Account Type
        allowed_types = {t.value for t in AccType}
        if acc_type not in allowed_types:
            raise ValueError(f"Invalid account type '{acc_type}'. Must be one of {allowed_types}")
        self._acc_type = acc_type

        # Handle string or datetime objects safely (especially during reconstruction)
        if isinstance(created_at, str):
            self._created_at = datetime.fromisoformat(created_at)
        else:
            self._created_at = created_at if created_at else datetime.now(timezone.utc).replace(microsecond=0)

        # Mutable properties
        self.acc_name = acc_name
        self.balance = amount  # Triggers the property setter to enforce invariants
        self._acc_status = AccStat.ACTIVE.value

    # --- WRITE-ONCE PROPERTIES (No Setters) ---

    @property
    def id(self) -> str:
        return self._id

    @property
    def acc_type(self) -> str:
        return self._acc_type

    @property
    def created_at(self) -> datetime:
        return self._created_at

    # --- MUTABLE PROPERTIES ---

    @property
    def balance(self) -> int:
        return self._balance

    @balance.setter
    def balance(self, amount: int):
        if amount < 0:
            raise ValueError("Account balance cannot drop below $0.00.")
        self._balance = amount

    @property
    def acc_status(self) -> str:
        return self._acc_status

    @acc_status.setter
    def acc_status(self, value: str):
        allowed_statuses = {status.value for status in AccStat}
        if value not in allowed_statuses:
            raise ValueError(f"Invalid account status. Must be one of {allowed_statuses}")
        self._acc_status = value

    # --- FACTORY & SERIALIZATION ---

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """To reconstruct account objects from dictionaries"""
        instance = cls(
            id = data["id"],
            acc_name = data["acc_name"],
            acc_type = data["acc_type"],
            amount = data["balance"],
            created_at = data["created_at"])
        # Re-assign status stored in database/dictionary
        if "acc_status" in data:
            instance.acc_status = data["acc_status"]
        return instance
    
    def to_dict(self) -> AccDict:
        """Returns account attributes as dictionaries."""
        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "balance": self.balance,
            "acc_type": self.acc_type,
            "acc_status": self.acc_status,
            "created_at": self.created_at.isoformat()
        }

    # --- BUSINESS LOGIC METHODS ---

    def show_balance(self):
        """Displays account's current balance"""
        print("\n  CURRENT BALANCE")
        print("  " + "—" * 25)
        print(f"  Available Funds:  ${self.balance:,.2f}")
        print("  " + "—" * 25 + "\n")

    def credit(self, amt: int):
        """Credits account with specified amount"""
        if self.acc_status == AccStat.INACTIVE.value:
            raise PermissionError("Transaction rejected: Cannot credit an inactive account.")
        self.balance += amt

    def debit(self, amt: int):
        """Debits account by specified amount"""
        if self.acc_status == AccStat.INACTIVE.value:
            raise PermissionError("Transaction rejected: Cannot debit an inactive account.")
        self.balance -= amt

    def deposit(self):
        """Handles account deposit"""
        if self.acc_status == AccStat.INACTIVE.value:
            print("\n  [!] Error: Transactions are locked on inactive accounts.")
            return

        print("DEPOSIT")
        amt = input("  Enter deposit amount → ").strip()

        try:
            deposit_amt = validate_amount(amt)
        except InvalidAmountError as err:
            print(err)
            return

        if deposit_amt == 0:
            print("\n  [!] Transaction canceled: Amount must be greater than $0.00.")
            return

        self.credit(deposit_amt)
        print(f"\n  [✓] Transaction successful. New Balance: ${self.balance:,.2f}\n")
        return deposit_amt

    def withdraw(self):
        if self.acc_status == AccStat.INACTIVE.value:
            print("\n  [!] Error: Transactions are locked on inactive accounts.")
            return

        print("WITHDRAWAL")
        amt = input("  Enter withdrawal amount → ").strip()
        
        try:
            expense_amt = validate_amount(amt)
        except InvalidAmountError as err:
            print(err)
            return

        if expense_amt == 0:
            print("\n  [!] Transaction canceled: Amount must be greater than $0.00.")
            return

        if expense_amt > self.balance:
            print("\n  [!] Error: Transaction limit exceeded.")
            return

        try:
            category = get_category()
        except InvalidOptionError as err:
            print(err)
            return

        self.debit(expense_amt)
        print(f"\n  [✓] Transaction successful. New Balance: ${self.balance:,.2f}\n")
        return expense_amt, category

    def deactivate(self):
        if self.balance > 0:
            print("\n  [i] Account must be empty before it can be deactivated.\n")
            return AccDashState.ACC_DASH.value
        
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
            return AccDashState.RETURN.value

        print("\n  [i] Operation canceled. Returning...\n")
        return AccDashState.ACC_DASH.value

    def reactivate(self):
        """Reactivates an inactive account, restoring functionality."""
        if self.acc_status == AccStat.ACTIVE.value:
            raise ValueError("State Conflict: Account is already active.")
        
        self.acc_status = AccStat.ACTIVE.value
