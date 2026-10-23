from enum import Enum
from typing import TypedDict

class MenuState(Enum):
    DASHBOARD = "dashboard"
    EXIT = "exit"
    CREATE_ACCOUNT = "create_account"

class AccDict(TypedDict):
    id: str
    acc_name: str
    created_at: str
    status: str
    acc_type: str
    acc_bal: int

class TrxDict(TypedDict):
    pass

class TrackerData(TypedDict):
    accounts: dict[str, AccDict]
    transactions: list[TrxDict]

class AccStat(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class AccType(Enum):
    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"