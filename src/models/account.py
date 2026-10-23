from models.types import AccStat, AccDict
from datetime import datetime, timezone

class Account:
    def __init__(
        self,
        id: str,
        account_name: str,
        acc_type: str,
        amount: int
    ):
        self.id = id
        self.account_name = account_name
        self.balance = amount
        self.account_type = acc_type
        self.account_status = AccStat.ACTIVE.value
        self.created_at = datetime.now(timezone.utc).replace(microsecond=0)

    def to_dict(self) -> AccDict:
        return {
            "id": self.id,
            "acc_name": self.account_name,
            "acc_bal": self.balance,
            "acc_type": self.account_type,
            "status": self.account_status,
            "created_at": self.created_at.isoformat(),
        }
