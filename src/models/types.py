"""Contains schemas, valid states(to prevent passing string literals around) and ensures consitent type hinting."""


from __future__ import annotations
from enum import Enum
from typing import TypedDict, TYPE_CHECKING
from datetime import datetime

# To prevent circular import error when importing Account class
if TYPE_CHECKING:
    from models.account import Account

class MenuState(Enum):
    """Used in the tracker runner to define where you are at any point in the app
    
    Values:
    - DASHBOARD - Displays the main menu options
    - EXIT - Closes the app
    - CREATE_ACCOUNT - Routes to account creation
    - LIST_ACCOUNTS - Routes to accounts list
    - TRANSFER - Routes to funds transfer
    - ACC_DASHBOARD - Routes to account dashboard
    - TRANSACTIONS - Routes to transactions list
    - REPORTS - Routes to reports
    
    Usage:
      state = MenuState.DASHBOARD.value
      print(state)
    
    Output => dashboard"""

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
    """Used to define account dashboard state that determines where you are at anypoint in when inspecting an account.
    
    Values:
    - ACC_DASH - Displays the account dashboard options
    - BALANCE - Routes to account balance
    - DEPOSIT - Routes to deposit
    - WITHDRWAL - Routes to withdrawal
    - DEACTIVATE - Routes to account deactivation
    - RETURN - Routes to the main menu

    Usage:
      acc_dash_state = AccdashState.BALANCE.value
      print(acc_state)
    
    Output => balance
    """
    ACC_DASH = "acc_dash"
    BALANCE = "balance"
    DEPOSIT = "deposit"
    WITHDRWAL = "withdrawal"
    DEACTIVATE = "deactivate"
    RETURN = "return"

class AccDict(TypedDict):
    "Account dictionary schema for JSON"
    id: str
    acc_name: str
    balance: int
    acc_type: str
    acc_status: str
    created_at: str | datetime

class TrxDict(TypedDict):
    "Base transaction dictionary schema for JSON shared accross all transaction types."
    id: str
    amount: int
    timestamp: datetime | str

class TransferTrxDict(TrxDict):
    "Transfer transaction dictionary schema for JSON"
    source_acc_id: str
    target_acc_id: str
    transaction_type: str

class DepositTrxDict(TrxDict):
    "Deposit transaction dictionary schema for JSON"
    acc_id: str
    transaction_type: str

class WithdrawalTrxDict(TrxDict):
    "Withdrawal transaction dictionary schema for JSON"
    category: str
    transaction_type: str

class TrackerData(TypedDict):
    """Global data schema for app"""
    accounts: dict[str, Account]
    transactions: list[TransferTrxDict | DepositTrxDict | WithdrawalTrxDict]

class JsonTrackerData(TypedDict):
    """Global data schema for app for JSON type hinting"""
    accounts: dict[str, AccDict]
    transactions: list[TransferTrxDict | DepositTrxDict | WithdrawalTrxDict]

class AccStat(Enum):
    """Valid account states
    
    Values:
    - ACTIVE - account is active
    - INACTIVE - account has been deactivated
    
    Usage:
      acc_status = AccStat.ACTIVE.value
      print(acc_status)
    
    Output => active"""

    ACTIVE = "active"
    INACTIVE = "inactive"

class AccType(Enum):
    """Valid account types
        
        Values:
        - BANK - bank account
        - CASH - cash account
        - SAVINGS - savings account
        - MOBILE- mobile account
        
        Usage:
          acc_type = AccType.CASH.value
          print(acc_type)
        
        Output => cash"""
    
    BANK = "bank"
    CASH = "cash"
    SAVINGS = "savings"
    MOBILE = "mobile"

class TrxType(Enum):
    """Valid account types
            
        Values:
        - TRANSFER - indicates a transfer transaction
        - WITHDRAW - indicates a withdrawal transaction
        - DEPOSIT - indicates a deposit transaction
        
        Usage:
            transaction_type = TrxType.TRANSFER.value
            print(transaction_type)
        
        Output => transfer"""
    
    TRANSFER = "transfer"
    WITHDRAW = "withdraw"
    DEPOSIT = "deposit"