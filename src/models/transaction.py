"""Transaction domain models for the Finance Tracker application.

Defines an immutable data layer structure modeling financial transfers, 
deposits, and withdrawals using Python data classes.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Self

from models.types import DepositTrxDict, TransferTrxDict, TrxDict, TrxType, WithdrawalTrxDict


def generate_timestamp() -> datetime:
    """Generates a timezone-aware UTC datetime truncated to seconds."""
    return datetime.now(timezone.utc).replace(microsecond=0)


@dataclass(frozen=True, kw_only=True)
class Transaction:
    """Base immutable schema for all financial transaction entities."""

    id: str
    amount: int
    timestamp: datetime | str = field(default_factory=generate_timestamp)

    @classmethod
    def parse_json(cls, data: dict[str, Any]) -> TrxDict:
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

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Hydrates a serialized dictionary payload into a live TransferTrx instance."""
        base_data = cls.parse_json(data)
        return cls(
            id=base_data["id"],
            amount=base_data["amount"],
            timestamp=base_data["timestamp"],
            source_acc_id=data["source_acc_id"],
            target_acc_id=data["target_acc_id"],
            transaction_type=data.get("transaction_type", TrxType.TRANSFER.value),
        )

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

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Hydrates a serialized dictionary payload into a live DepositTrx instance."""
        base_data = cls.parse_json(data)
        return cls(
            id=base_data["id"],
            amount=base_data["amount"],
            timestamp=base_data["timestamp"],
            acc_id=data["acc_id"],
            transaction_type=data.get("transaction_type", TrxType.DEPOSIT.value),
        )

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

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> Self:
        """Hydrates a serialized dictionary payload into a live WithdrawalTrx instance."""
        base_data = cls.parse_json(data)
        return cls(
            id=base_data["id"],
            amount=base_data["amount"],
            timestamp=base_data["timestamp"],
            category=data["category"],
            transaction_type=data.get("transaction_type", TrxType.WITHDRAW.value),
        )

    def to_dict(self) -> WithdrawalTrxDict:
        """Serializes instance fields into a data-transfer structure."""
        return {
            "id": self.id,
            "amount": self.amount,
            "timestamp": self.timestamp,
            "category": self.category,
            "transaction_type": self.transaction_type,
        }
