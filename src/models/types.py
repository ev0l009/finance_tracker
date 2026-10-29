"""Data schemas, enum states, and type-hinting structures for the application.

This module centralizes system-wide type definitions, ensuring consistent 
data schemas (via TypedDict) and eliminating raw string literals (via Enum).
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from models.account import Account


class MenuState(Enum):
    """Application-level navigation states for the primary loop."""

    DASHBOARD = "dashboard"
    EXIT = "exit"
    CREATE_ACCOUNT = "create_account"
    LIST_ACCOUNTS = "list_accounts"
    TRANSFER = "transfer"
    ACC_DASHBOARD = "acc_dashboard"
    TRANSACTIONS = "transactions"
    REPORTS = "reports"
    REACTIVATE_ACC = "reactivate"


class AccDashState(Enum):
    """Navigation states for individual account inspection dashboards."""

    ACC_DASH = "acc_dash"
    BALANCE = "balance"
    DEPOSIT = "deposit"
    WITHRAWAL = "withdrawal"
    DEACTIVATE = "deactivate"
    RETURN = "return"


class AccDict(TypedDict):
    """Serialization schema for individual accounts stored in JSON."""

    id: str
    acc_name: str
    balance: int
    acc_type: str
    acc_status: str
    created_at: str | datetime


class TrxDict(TypedDict):
    """Base serialization schema for all application transactions."""

    id: str
    amount: int
    timestamp: datetime | str


class TransferTrxDict(TrxDict):
    """Serialization schema for peer-to-peer account transfers."""

    source_acc_id: str
    target_acc_id: str
    transaction_type: str


class DepositTrxDict(TrxDict):
    """Serialization schema for account funding deposits."""

    acc_id: str
    transaction_type: str


class WithdrawalTrxDict(TrxDict):
    """Serialization schema for capital withdrawals and expenses."""

    category: str
    transaction_type: str


# Aggregate structural types for internal system and external JSON data maps
AnyTransactionDict = TransferTrxDict | DepositTrxDict | WithdrawalTrxDict


class TrackerData(TypedDict):
    """In-memory core application data map."""

    accounts: dict[str, Account]
    transactions: list[AnyTransactionDict]


class JsonTrackerData(TypedDict):
    """Serialized storage map matching the final output JSON structure."""

    accounts: dict[str, AccDict]
    transactions: list[AnyTransactionDict]


class AccStat(Enum):
    """Lifecycle states for operational accounts."""

    ACTIVE = "active"
    INACTIVE = "inactive"


class AccType(Enum):
    """Supported underlying storage classification for accounts."""

    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"


class TrxType(Enum):
    """Financial tracking action classifications."""

    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEPOSIT = "deposit"
