"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from exceptions import InvalidIDError, InvalidAmountError, SameAccountTransferError, InvalidTransactionTypeError, InvalidCategoryError

from models.types import TrxType, ExpCatOpts, DepositTrxDict, TransferTrxDict, TrxDict, WithdrawalTrxDict


def generate_timestamp() -> datetime:
    """Generates a timezone-aware UTC datetime truncated to seconds."""
    return datetime.now(timezone.utc).replace(microsecond=0)

@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Base immutable schema for all financial transaction entities."""
    id: str
    amount: int
    timestamp: datetime | str = field(default_factory=generate_timestamp)

    def __post_init__(self):
        if not self.id.strip():
            raise InvalidIDError("Transaction ID cannot be empty")
        if type(self.amount) is not int:
            raise InvalidAmountError("Amount must be a valid whole number integer.")
        if self.amount < 0:
            raise InvalidAmountError("Amount cannot be a negative value.")

    @classmethod
    def parse_json(cls, data: TrxDict) -> TrxDict:
        """Extracts and sanitizes base fields from a raw dictionary payload."""
        return {
            "id": data["id"],
            "amount": data["amount"],
            "timestamp": data.get("timestamp") or generate_timestamp(),
        }


@dataclass(frozen=True, kw_only=True)
class TransferTrx(Transaction):
    """Immutable ledger record representing money moved between two internal accounts."""

    source_acc_id: str
    target_acc_id: str
    transaction_type: str = TrxType.TRANSFER.value

    def __post_init__(self):
        if not self.source_acc_id.strip() or not self.target_acc_id.strip():
            raise InvalidIDError("Account ID cannot be empty")
        if self.source_acc_id == self.target_acc_id:
            raise SameAccountTransferError("Source and target accounts cannot be thesame for a transfer transaction.")
        if self.transaction_type != TrxType.TRANSFER.value:
            raise InvalidTransactionTypeError("Transaction type must be `transfer` for transfer transactions.")

    def to_dict(self) -> TransferTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "source_acc_id": self.source_acc_id,
            "target_acc_id": self.target_acc_id,
            "transaction_type": self.transaction_type,
        }


@dataclass(frozen=True, kw_only=True)
class DepositTrx(Transaction):
    """Immutable ledger record representing balance inflows added to an account."""

    acc_id: str
    transaction_type: str = TrxType.DEPOSIT.value

    def __post_init__(self):
        if not self.acc_id.strip():
            raise InvalidIDError("Account ID cannot be empty")
        if self.transaction_type != TrxType.DEPOSIT.value:
            raise InvalidTransactionTypeError("Transaction type must be `deposit` for deposit transactions.")

    def to_dict(self) -> DepositTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "acc_id": self.acc_id,
            "timestamp": self.timestamp,
            "transaction_type": self.transaction_type,
        }


@dataclass(frozen=True, kw_only=True)
class WithdrawalTrx(Transaction):
    """Immutable ledger record tracking out-of-pocket expenses or out-of-system outflows."""


    category: str
    transaction_type: str = TrxType.WITHDRAW.value
    acc_id: str

    def __post_init__(self):
        
        
        if self.transaction_type != TrxType.WITHDRAW.value:
            raise InvalidTransactionTypeError("Transaction type must be `withdrawal` for withdrawal transactions.")
        if not self.acc_id.strip():
            raise InvalidIDError("Account ID cannot be empty")
        if self.category not in [item.value for item in ExpCatOpts]:
            raise InvalidCategoryError("Invalid category.")

    def to_dict(self) -> WithdrawalTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "category": self.category,
            "acc_id": self.acc_id,
            "transaction_type": self.transaction_type
        }
