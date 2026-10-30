"""Account domain models for the Finance Tracker application.

Defines the core operational Account entity, ensuring strict maintenance of 
financial invariants, lifecycle state machines, and safe JSON serialization.
"""

from datetime import datetime, timezone
from typing import Any, Self

from models.types import AccDict, AccStat, AccType

from exceptions import InvalidIDError, AccNameError, InvalidAccountTypeError, InvalidAmountError, InvalidAccountStatusError

class Account:
    """Encapsulates account configurations, state constraints, and balance updates."""

    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        amount: int,
        created_at: datetime | str | None = None,
    ):
        if not id or not id.strip():
            raise InvalidIDError("Account ID cannot be empty.")
        self._id = id

        if not acc_name.strip():
            raise AccNameError("Account name cannot be empty.")
        if len(acc_name.strip()) < 3:
            raise AccNameError("Account name cannot be less three characters.")
        self.acc_name = acc_name

        allowed_types = {t.value for t in AccType}
        if acc_type not in allowed_types:
            raise InvalidAccountTypeError(f"Invalid account type '{acc_type}'. Must be one of {allowed_types}")
        self._acc_type = acc_type

        if isinstance(created_at, str):
            self._created_at = datetime.fromisoformat(created_at)
        else:
            self._created_at = created_at if created_at else datetime.now(timezone.utc).replace(microsecond=0)

        self.balance = amount  
        self._acc_status = AccStat.ACTIVE.value

    # --- WRITE-ONCE INVARIANT PROPERTIES ---
 
    @property
    def id(self) -> str:
        """str: The unique, unalterable identifier for this account instance."""
        return self._id

    @property
    def acc_type(self) -> str:
        """str: The classification type (e.g., bank, cash, savings) assigned on creation."""
        return self._acc_type

    @property
    def created_at(self) -> datetime:
        """datetime: The immutable record creation timestamp."""
        return self._created_at

    # --- MUTABLE LAYER PROPERTIES ---

    @property
    def balance(self) -> int:
        """int: The current stored monetary asset value."""
        return self._balance

    @balance.setter
    def balance(self, amount: int) -> None:
        if type(amount) is not int:
            raise InvalidAmountError("Amount must be a valid whole number integer.")
        if amount < 0:
            raise InvalidAmountError("Account balance cannot drop below zero.")
        self._balance = amount

    @property
    def acc_status(self) -> str:
        """str: The operational availability lifecycle state of the account."""
        return self._acc_status

    @acc_status.setter
    def acc_status(self, value: str) -> None:
        allowed_statuses = {status.value for status in AccStat}
        if value not in allowed_statuses:
            raise InvalidAccountStatusError(f"Invalid account status. Must be one of {allowed_statuses}")
        self._acc_status = value

    # --- FACTORY & SERIALIZATION ---

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Reconstructs a live Account object instance from a storage data map."""
        instance = cls(
            id=data["id"],
            acc_name=data["acc_name"],
            acc_type=data["acc_type"],
            amount=data["balance"],
            created_at=data["created_at"],
        )
        if "acc_status" in data:
            instance.acc_status = data["acc_status"]
        return instance

    def to_dict(self) -> AccDict:
        """Serializes current instance state into a plain dictionary data map."""
        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "balance": self.balance,
            "acc_type": self.acc_type,
            "acc_status": self.acc_status,
            "created_at": self.created_at.isoformat(),
        }

    # --- BUSINESS CORE METHODS ---

    def credit(self, amt: int) -> None:
        """Increments account assets by a specified quantity.

        Raises:
            PermissionError: If the underlying account status is currently inactive.
        """
        if self.acc_status == AccStat.INACTIVE.value:
            raise PermissionError("Transaction rejected: Cannot credit an inactive account.")
        self.balance += amt

    def debit(self, amt: int) -> None:
        """Decrements account assets by a specified quantity.

        Raises:
            PermissionError: If the account is inactive.
            ValueError: If the withdrawal exceeds available funds.
        """
        if self.acc_status == AccStat.INACTIVE.value:
            raise PermissionError("Transaction rejected: Cannot debit an inactive account.")
        if amt > self.balance:
            raise ValueError("Transaction rejected: Insufficient available funds.")
        self.balance -= amt

    def deactivate_account(self) -> bool:
        """Attempts to change status to inactive if balance invariants allow.

        Returns:
            bool: True if the account was successfully deactivated, False otherwise.
        """
        if self.balance > 0:
            return False
        self.acc_status = AccStat.INACTIVE.value
        return True

    def reactivate(self) -> None:
        """Restores full operational status to an inactive account instance.

        Raises:
            ValueError: If the account state is already marked active.
        """
        if self.acc_status == AccStat.ACTIVE.value:
            raise ValueError("State Conflict: Account is already active.")
        self.acc_status = AccStat.ACTIVE.value
