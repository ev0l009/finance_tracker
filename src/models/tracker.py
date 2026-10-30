"""Core workflow orchestration engine for the Finance Tracker application.

Coordinates business workflows, updates states across system components,
and manages transaction event histories within the application.
"""

import secrets
import string
from typing import Final

from exceptions import AccNameError, InvalidAmountError, InvalidOptionError, NullEligibleAccountsError
from models.account import Account
from models.transaction import DepositTrx, TransferTrx, WithdrawalTrx
from models.types import AccStat, TrackerData, TrxType, AccDashState
from ui import get_account_type, select_acc, get_acc_dash_state
from utils import validate_acc_name, validate_amount

from file_manager.storage import save_tracker_data, load_tracker_data

class Tracker:
    """Orchestrates high-level system functions and manages memory data sets."""

    # Constant string anchors for memory map structural indexing
    TRX: Final[str] = "transactions"
    ACC: Final[str] = "accounts"

    def __init__(self) -> None:
        """Initializes an empty transient storage map for the tracker lifecycle."""
        self.data: TrackerData = {
            "accounts": {},
            "transactions": []
        }

    def generate_id(self, prefix: str, field: str) -> str:
        """Generates a unique, non-colliding cryptographically secure identity key.

        Creates an 8-character string formatted as 'prefix_XXXXX' using a random
        pool of letters and numbers. Employs a non-recursive loop to safely prevent
        identifier collisions.

        Args:
            prefix: The tracking indicator category name (e.g., 'acc', 'trx').
            field: The structural field name within tracking storage datasets.

        Returns:
            str: A globally unique, non-colliding identity string.
        """
        pool = string.ascii_letters + string.digits
        
        while True:
            suffix = "".join(secrets.choice(pool) for _ in range(5))
            gen_id = f"{prefix}_{suffix}"

            # Verify structural isolation uniqueness to prevent duplicates
            if field == self.ACC and gen_id not in self.data["accounts"]:
                return gen_id
            
            if field == self.TRX:
                # Deduplicate transactions list tracking records
                if not any(trx["id"] == gen_id for trx in self.data["transactions"]):
                    return gen_id

    def create_account(self) -> None:
        """Guides user input workflows to validate and construct a new Account."""
        print("\n  ACCOUNT CREATION")
        print("  " + "—" * 20)

        # Build map constraint targets to accurately prevent name collisions
        existing_names = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
        }

        raw_name = input("  Enter account name → ").strip()
        try:
            valid_acc_name = validate_acc_name(raw_name, existing_names)
        except AccNameError as err:
            print(f"\n  [!] Error: {err}")
            return

        try:
            acc_type = get_account_type()
        except InvalidOptionError as err:
            print(f"\n  [!] Selection Error: {err}")
            return

        print("\n  [i] Press Enter to start with an empty balance ($0.00).")
        raw_amount = input("  Enter starting balance → ").strip()

        try:
            start_balance = validate_amount(raw_amount)
        except InvalidAmountError as err:
            print(f"\n  [!] Validation Error: {err}")
            return

        new_acc_id = self.generate_id("acc", self.ACC)
        new_account = Account(
            id=new_acc_id,
            acc_name=valid_acc_name,
            acc_type=acc_type,
            amount=start_balance
        )
        
        self.data["accounts"][new_acc_id] = new_account

        # Generate a formal funding event record for non-zero opening balances
        if start_balance > 0:
            trx_id = self.generate_id("trx", self.TRX)
            funding_event = DepositTrx(
                id=trx_id,
                amount=start_balance,
                acc_id=new_acc_id
            ).to_dict()

            self.data["transactions"].append(funding_event)

        print("\n  [✓] Account creation successful.\n")


    def list_accounts(self) -> None:
        """Renders a formatted text grid table displaying active accounts in memory."""
        print("\n  ACTIVE ACCOUNTS")
        print("  " + "—" * 58)

        active_accounts = [
            acc
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        ]
        
        if not active_accounts:
            print("  [i] There are no active accounts right now.\n")
            return

        print(f"  {'Account Name':<16} {'Account ID':<12} {'Type':<12} {'Balance':>12}")
        print("  " + "—" * 58)
        
        for acc in active_accounts:
            # Prevent grid breakage by truncating names longer than 14 characters
            if len(acc.acc_name) > 14:
                name_trunc = f"{acc.acc_name.title()[:14]}.."
            else:
                name_trunc = acc.acc_name.title()
                
            type_str = acc.acc_type.capitalize()
            balance_str = f"${acc.balance:,.2f}"
            
            print(f"  {name_trunc:<16} {acc.id:<12} {type_str:<12} {balance_str:>12}")
            
        print("  " + "—" * 58 + "\n")

    def transfer(self) -> None:
        """Coordinates a secure fund transfer workflow between two active accounts."""
        print("\n  FUND TRANSFER")
        print("  " + "—" * 20)

        # Build list of active accounts eligible for transfers
        active_acc_map = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        }

        if len(active_acc_map) < 2:
            print("  [!] Action unavailable: At least 2 active accounts are required to transfer funds.\n")
            return

        try:
            sender_acc_id = select_acc(
                acc_map=active_acc_map,
                heading="Source Account"
            )
        except (InvalidOptionError, NullEligibleAccountsError) as err:
            print(f"\n  [!] Selection canceled: {err}")
            return

        sender_acc = self.data["accounts"][sender_acc_id]

        raw_amount = input("  Enter transfer amount → ").strip()
        try:
            transfer_amt = validate_amount(raw_amount)
        except InvalidAmountError as err:
            print(f"\n  [!] Validation Error: {err}")
            return

        if transfer_amt <= 0:
            print("\n  [!] Transaction canceled: Transfer amount must be greater than $0.00.\n")
            return

        if transfer_amt > sender_acc.balance:
            print("\n  [!] Error: Insufficient available funds for this transfer request.\n")
            return

        try:
            receiver_acc_id = select_acc(
                acc_map=active_acc_map,
                id_to_skip=sender_acc_id,
                heading="Target Account"
            )
        except (InvalidOptionError, NullEligibleAccountsError) as err:
            print(f"\n  [!] Selection canceled: {err}")
            return

        receiver_acc = self.data["accounts"][receiver_acc_id]

        try:
            # Enforce safety policies by leveraging our core model method behaviors
            sender_acc.debit(transfer_amt)
            receiver_acc.credit(transfer_amt)
        except (PermissionError, ValueError) as domain_err:
            print(f"\n  [!] Ledger Processing Error: {domain_err}\n")
            return

        # Generate transaction ledger items after balances are verified
        trx_id = self.generate_id("trx", self.TRX)
        transfer_record = TransferTrx(
            id=trx_id,
            amount=transfer_amt,
            source_acc_id=sender_acc_id,
            target_acc_id=receiver_acc_id
        ).to_dict()
        
        self.data["transactions"].append(transfer_record)
        print("\n  [✓] Transfer completed successfully.\n")


    def acc_dashboard(self) -> None:
        """Manages individual account operations via an interactive navigation loop."""
        active_acc_map = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        }

        try:
            acc_id = select_acc(acc_map=active_acc_map, heading="Inspect Account")
        except (InvalidOptionError, NullEligibleAccountsError) as err:
            print(f"\n  [!] Access Denied: {err}")
            return

        acc = self.data["accounts"][acc_id]
        state = AccDashState.ACC_DASH.value

        while state != AccDashState.RETURN.value:
            if state == AccDashState.ACC_DASH.value:
                state = get_acc_dash_state(acc.acc_name)

            elif state == AccDashState.BALANCE.value:
                acc_bal = acc.balance
                print("\n  CURRENT BALANCE")
                print("  " + "—" * 25)
                print(f"  Available Funds:  ${acc_bal:,.2f}")
                print("  " + "—" * 25 + "\n")
                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.DEPOSIT.value:
                print("\n  ACCOUNT DEPOSIT")
                raw_amt = input("  Enter deposit amount → ").strip()
                try:
                    deposit_amt = validate_amount(raw_amt)
                    if deposit_amt <= 0:
                        print("\n  [!] Error: Deposit amount must be greater than $0.00.")
                    else:
                        acc.credit(deposit_amt)
                        trx_id = self.generate_id("trx", self.TRX)
                        deposit_record = DepositTrx(
                            id=trx_id,
                            acc_id=acc_id,
                            amount=deposit_amt
                        ).to_dict()
                        
                        self.data["transactions"].append(deposit_record)
                        print(f"\n  [✓] Deposit successful. New Balance: ${acc.balance:,.2f}")
                except (InvalidAmountError, PermissionError) as err:
                    print(f"\n  [!] Transaction failed: {err}")
                
                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.WITHRAWAL.value:
                print("\n  ACCOUNT WITHDRAWAL")
                raw_amt = input("  Enter withdrawal amount → ").strip()
                try:
                    expense_amt = validate_amount(raw_amt)
                    if expense_amt <= 0:
                        print("\n  [!] Error: Withdrawal amount must be greater than $0.00.")
                    elif expense_amt > acc.balance:
                        print("\n  [!] Error: Insufficient available funds.")
                    else:
                        from ui import get_category  # Local inline import to avoid circular ties
                        category = get_category()
                        
                        acc.debit(expense_amt)
                        trx_id = self.generate_id("trx", self.TRX)
                        withdrawal_record = WithdrawalTrx(
                            id=trx_id,
                            category=category,
                            amount=expense_amt
                        ).to_dict()
                        
                        self.data["transactions"].append(withdrawal_record)
                        print(f"\n  [✓] Withdrawal successful. New Balance: ${acc.balance:,.2f}")
                except (InvalidAmountError, PermissionError, InvalidOptionError) as err:
                    print(f"\n  [!] Transaction failed: {err}")
                
                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.DEACTIVATE.value:
                print("\n  ACCOUNT DEACTIVATION")
                print("  " + "—" * 35)
                print("  ⚠️  Notice: Deactivating this account locks all features")
                print("      until it is reactivated.")
                print("  1. Proceed with Deactivation")
                print("  2. Cancel and Return\n")
                
                choice = input("  Select option (1-2) → ").strip()
                if choice == "1":
                    success = acc.deactivate_account()
                    if success:
                        print("\n  [✓] Account deactivated successfully.\n")
                        state = AccDashState.RETURN.value
                    else:
                        print("\n  [!] Error: Account must be empty ($0.00) before deactivation.\n")
                        state = AccDashState.ACC_DASH.value
                else:
                    state = AccDashState.ACC_DASH.value

    def list_transactions(self) -> None:
        """Renders a structured grid report of historical transaction records."""
        if not self.data["transactions"]:
            print("\n  [!] No transactions found in this ledger.\n")
            return

        print("\n  TRANSACTION HISTORY")
        print("  " + "—" * 45)
        print(f"  {'ID':<13} {'Type':<11} {'Amount':>16}")
        print("  " + "—" * 45)

        for trx in self.data["transactions"]:
            trx_id = trx["id"]
            trx_type = trx["transaction_type"].capitalize()
            
            # Explicit directional labeling based on specific financial context types
            if trx["transaction_type"] == TrxType.DEPOSIT.value:
                amt_str = f"+${trx['amount']:,.2f}"
            elif trx["transaction_type"] == TrxType.TRANSFER.value:
                amt_str = f"⇄ ${trx['amount']:,.2f}"
            else:
                amt_str = f"-${trx['amount']:,.2f}"

            print(f"  {trx_id:<13} {trx_type:<11} {amt_str:>16}")

        print("  " + "—" * 45 + "\n")

    def reports(self) -> None:
        """Generates comprehensive aggregated summaries of global accounting metrics."""
        active_accs = [
            acc for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        ]

        net_balance = sum(acc.balance for acc in active_accs)
        total_income = sum(
            t["amount"] for t in self.data["transactions"]
            if t["transaction_type"] == TrxType.DEPOSIT.value
        )
        total_expense = sum(
            t["amount"] for t in self.data["transactions"]
            if t["transaction_type"] == TrxType.WITHDRAW.value
        )

        expense_category: dict[str, int] = {}
        for trx in self.data["transactions"]:
            if trx["transaction_type"] == TrxType.WITHDRAW.value:
                cat = trx["category"].title() # type: ignore
                expense_category[cat] = expense_category.get(cat, 0) + trx["amount"] # type: ignore

        print("\n  FINANCIAL REPORT OVERVIEW")
        print("  " + "—" * 35)
        print(f"  Net Total Balance:  ${net_balance:,.2f}")
        print(f"  Total Income (+):   ${total_income:,.2f}")
        print(f"  Total Expenses (-): ${total_expense:,.2f}")
        print("  " + "—" * 35)

        print("\n  EXPENSES BY CATEGORY")
        print("  " + "—" * 35)
        
        if not expense_category:
            print("  (No expense transactions logged yet)")
        else:
            for cat, amt in expense_category.items():
                print(f"  {cat:<18} ${amt:>12,.2f}")
                
        print("  " + "—" * 35 + "\n")

    def reactivate_acc(self) -> None:
        """Prompts for and safely activates a disabled account instance."""
        inactive_accs_map = {
            acc_id: acc.acc_name
            for acc_id, acc in self.data["accounts"].items()
            if acc.acc_status == AccStat.INACTIVE.value
        }

        if not inactive_accs_map:
            print("\n  [i] There are no inactive accounts.\n")
            return

        try:
            inactive_acc_id = select_acc(
                acc_map=inactive_accs_map,
                heading="Account Reactivation"
            )
        except (InvalidOptionError, NullEligibleAccountsError) as err:
            print(f"\n  [!] Activation Canceled: {err}")
            return

        acc = self.data["accounts"][inactive_acc_id]
        
        try:
            acc.reactivate()
            print(f"\n  [✓] Account '{acc.acc_name}' (ID: {acc.id}) successfully reactivated!\n")
        except ValueError as err:
            print(f"\n  [!] State Conflict: {err}")
    
    def save(self) -> None:
        """Serializes and saves live records to external JSON storage file pools."""
        save_tracker_data(self.data)

    def load(self) -> None:
        """Hydrates the application layer using files retrieved from storage layers."""
        self.data = load_tracker_data()
