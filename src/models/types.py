from enum import Enum
from typing import TypedDict
from datetime import datetime
from models.account import Account

class MenuState(Enum):
    DASHBOARD = "dashboard"
    EXIT = "exit"
    CREATE_ACCOUNT = "create_account"
    LIST_ACCOUNTS = "list_accounts"
    TRANSFER = "transfer"

class AccDict(TypedDict):
    id: str
    acc_name: str
    balance: int
    acc_type: str
    acc_status: str
    created_at: str | datetime

class TrxDict(TypedDict):
    id: str
    amount: int
    timestamp: datetime | str

class TransferTrxDict(TrxDict):
    source_acc_id: str
    target_acc_id: str
    transaction_type: str

class TrackerData(TypedDict):
    accounts: dict[str, Account]
    transactions: list[TrxDict]

class JsonTrackerData(TypedDict):
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

class TrxType(Enum):
    TRANSFER = "transfer"