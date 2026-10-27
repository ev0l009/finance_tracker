from datetime import datetime
from dataclasses import dataclass
from models.types import TrxDict, TransferTrxDict, TrxType

from typing import Any

@dataclass(frozen=True)
class Transaction:
    id: str
    amount: int
    timestamp: datetime

    @classmethod
    def from_json(cls, data: dict[str, Any]) -> TrxDict:
        ts = datetime.now().replace(microsecond=0).strftime("%Y/%m/%d, %H:%M:%S")

        return {
            "id": data["id"],
            "amount": data["amount"],
            "timestamp": ts
        }

@dataclass(frozen=True)
class TransferTrx(Transaction):
    source_acc_id: str
    target_acc_id: str

    @classmethod
    def from_json(cls, data: dict[str, Any]):
        base_data = super().from_json(data)

        return cls(
            **base_data,
            source_acc_id=data["source_account_id"],
            target_acc_id=data["target_acc_id"]
        )