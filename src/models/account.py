from models.types import AccStat, AccDict
from datetime import datetime, timezone

class Account:
    def __init__(
        self,
        id: str,
        acc_name: str,
        acc_type: str,
        amount: int
    ):
        self.id = id
        self.acc_name = acc_name
        self.balance = amount
        self.acc_type = acc_type
        self.acc_status = AccStat.ACTIVE.value
        self.created_at = datetime.now(timezone.utc).replace(microsecond=0)

    def to_dict(self) -> AccDict:
        return {
            "id": self.id,
            "acc_name": self.acc_name,
            "balance": self.balance,
            "acc_type": self.acc_type,
            "acc_status": self.acc_status,
            "created_at": self.created_at.strftime("%Y:%m:%d %H:%M:%S")
        }