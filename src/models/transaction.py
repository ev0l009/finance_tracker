from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any
from models.types import TrxDict, TrxType, TransferTrxDict, DepositTrxDict, WithdrawalTrxDict

def generate_timetamp() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)

@dataclass(frozen=True)
class Transaction():
    id: str
    amount: int
    timestamp: datetime | str = field(default_factory=generate_timetamp)

    @classmethod
    def parse_json(cls, data: dict[str, Any]) -> TrxDict:
        return {
            "id": data["id"],
            "amount": data["amount"],
            "timestamp": data.get("timestamp") or generate_timetamp()
        }

@dataclass(frozen=True, kw_only=True)
class TransferTrx(Transaction):
    source_acc_id: str
    target_acc_id: str
    transaction_type: str = TrxType.TRANSFER.value

    @classmethod
    def to_dict(cls, data: dict[str, Any]) -> TransferTrxDict:
        base_data = cls.parse_json(data)

        return {
            **base_data,
            "source_acc_id":data["source_acc_id"],
            "target_acc_id":data["target_acc_id"],
            "transaction_type": data["transaction_type"]
        }
    
@dataclass(frozen=True, kw_only=True)
class DepositTrx(Transaction):
    acc_id: str
    transaction_type: str = TrxType.DEPOSIT.value
    
    @classmethod
    def to_dict(cls, data: dict[str, Any]) -> DepositTrxDict:
        base_data = cls.parse_json(data)

        return {
            **base_data,
            "acc_id": data["acc_id"],
            "transaction_type": data["transaction_type"]
        }

@dataclass(frozen=True, kw_only=True)
class WithdrawalTrx(Transaction):
    category: str
    transaction_type: str = TrxType.WITHDRAW.value

    @classmethod
    def to_dict(cls, data: dict[str, Any]) -> WithdrawalTrxDict:
        base_data = cls.parse_json(data)

        return {
            **base_data,
            "category": data["category"],
            "transaction_type": data["transaction_type"]
        }