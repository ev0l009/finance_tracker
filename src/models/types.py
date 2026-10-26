from enum import Enum
from typing import TypedDict
from datetime import datetime

class MenuState(Enum):
    DASHBOARD = "dashboard"
    EXIT = "exit"
    CREATE_ACCOUNT = "create_account"
    LIST_ACCOUNTS = "list_accounts"

class AccDict(TypedDict):
    id: str
    acc_name: str
    balance: int
    acc_type: str
    acc_status: str
    created_at: str | datetime

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