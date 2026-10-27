from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Any
from models.types import TrxDict

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
            "timestamp": data["timestamp"]
        }

@dataclass(frozen=True, kw_only=True)
class TransferTrx(Transaction):
    source_acc_id: str
    target_acc_id: str

    @classmethod
    def from_json(cls, data: dict[str, Any]):
        base_data = cls.parse_json(data)

        return cls(
            **base_data,
            source_acc_id=data["source_acc_id"],
            target_acc_id=data["target_acc_id"]   
        )