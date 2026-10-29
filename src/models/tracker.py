"""Core of the app. Handles tracker initialization, validations and major tracker actions."""

from models.types import TrackerData, AccStat, AccDashState, TrxType
from ui import get_account_type, select_acc, get_acc_dash_state
import string
import secrets
from models.account import Account
from models.transaction import TransferTrx, DepositTrx, WithdrawalTrx
from file_manager.storage import save_tracker_data, load_tracker_data
from utils import validate_acc_name, validate_amount
from exceptions import AccNameError, InvalidOptionError, InvalidAmountError

class Tracker:
    """Initializes tracker object and handles major actionsn like account creation, loading and saving of tracker data, funds transafer and so on."""

    # Tracker data field constants for id generation
    TRX = "transactions"
    ACC = "accounts"
    
    def __init__(self):
        """Initializes a tracker object and holds tracker data in memory."""
        self.data: TrackerData = {
            "accounts": {},
            "transactions": []
        }

    def generate_id(self, preffix: str, field: str):
        """Generates a unique id for accounts and transactions. Generated IDs are a mixed of uppercase, lowercase alphabets and numbers of length 5 and preffix of length 3 along with the undersocre making 9 characters in all. 
        
        ### Args:
            - preffix `str`: id preffix
            - field `str`: tracker data field
            
        Returns generated id as str
        
        ### Usage:
        >>> trx_id = self.generate_id("trx", TRX)
        >>> print(trx_id)

        Output => trx_0qQ93"""

        # To collect all possible range of characters
        pool = string.ascii_letters + string.digits

        suffix = ''.join(secrets.choice(pool) for _ in range(5))
        
        gen_id = f"{preffix}_{suffix}"

        # To check for duplicates
        while gen_id in self.data[field]:
            self.generate_id(preffix, field)
        return gen_id

    def create_account(self):
        """Handles account creation and some validation."""

        print("\n  ACCOUNT CREATION")
        print("  " + "—" * 20)

        # To get account id and names for duplication check
        acc_map = {
            acc_id: acc.acc_name
            for acc_id, acc in self.data["accounts"].items()
        }

        acc_name = input("  Enter account name → ").strip()
        try:
            valid_acc_name = validate_acc_name(acc_name, acc_map)
        except AccNameError as err:
            print(err)
            return
        
        try:
            acc_type = get_account_type()
        except InvalidOptionError as err:
            print(err)
            return

        print("\n  [i] Press Enter to start with an empty balance ($0.00).")
        amt = input("  Enter starting balance → ").strip()

        try:
            start_amt = validate_amount(amt)
        except InvalidAmountError as err:
            print(err)
            return

        new_acc_id = self.generate_id("acc", self.ACC)

        new_acc = Account(
            new_acc_id,
            valid_acc_name,
            acc_type,
            start_amt
        )
        self.data["accounts"][new_acc_id] = new_acc

        # To log first non-zero deposit transaction
        if start_amt != 0:
            trx_id = self.generate_id("trx", self.TRX)
            trx = DepositTrx(
                id=trx_id,
                amount=start_amt,
                acc_id=new_acc_id
            ).to_dict()

            self.data["transactions"].append(trx)

        print("\n  [✓] Account creation successful.\n")

    def list_accounts(self):
        """Displays a list of active accounts with a few details."""

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
            name_trunc = acc.acc_name.title()[:14] + ".." if len(acc.acc_name) > 14 else acc.acc_name.title()
            type_str = acc.acc_type.capitalize()
            balance_str = f"${acc.balance:,.2f}"
            
            print(f"  {name_trunc:<16} {acc.id:<12} {type_str:<12} {balance_str:>12}")
            
        print("  " + "—" * 58 + "\n")

    def transfer(self):
        """Handles transfer of funds between accounts."""

        print("\n  FUND TRANSFER")
        print("  " + "—" * 20)

        if len(self.data["accounts"]) < 2:
            print("  [!] Action unavailable: You need at least 2 active accounts to make a transfer.\n")
            return

        # To get account names and account ids of active accounts
        acc_map = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        }

        try:
            sender_acc_id = select_acc(
                acc_map,
                "Source Account"
            )
        except InvalidOptionError as err:
            print(err)
            return

        sender_acc = self.data["accounts"][sender_acc_id]

        amt = input("  Enter transfer amount → ").strip()

        try:
            transfer_amt = validate_amount(amt)
        except InvalidAmountError as err:
            print(err)
            return

        if transfer_amt > sender_acc.balance:
            print("\n  [!] Error: Limit exceeded. Excessive transfers are not allowed.\n")
            return

        try:
            reciever_acc_id = select_acc(
                acc_map, 
                sender_acc_id,
                "Target Account"
            )
        except InvalidOptionError as err:
            print(err)
            return

        receiver_acc = self.data["accounts"][reciever_acc_id]

        sender_acc.balance -= transfer_amt
        receiver_acc.balance += transfer_amt

        trx_id = self.generate_id("trx", self.TRX)

        trx  = TransferTrx(
            id=trx_id,
            amount=transfer_amt,
            source_acc_id=sender_acc_id,
            target_acc_id=reciever_acc_id
        ).to_dict()
        self.data["transactions"].append(trx)
        
        print("\n  [✓] Transfer completed successfully.\n")

    def acc_dashboard(self):
        """Displays the account dashboard menu, routes based on state to account related actions."""

        # to get account name and  acccount id
        acc_map = {
            acc.id: acc.acc_name
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        }

        acc_id = select_acc(acc_map)
        acc = self.data["accounts"][acc_id]
        state = AccDashState.ACC_DASH.value
 
        while state != AccDashState.RETURN.value:
            if state == AccDashState.ACC_DASH.value:
                state = get_acc_dash_state(acc.acc_name)

            elif state == AccDashState.BALANCE.value:
                acc.show_balance()
                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.DEPOSIT.value:
                dep_amt = acc.deposit()
                if dep_amt:
                    trx_id = self.generate_id("trx", self.TRX)
                    trx =  DepositTrx(
                        id=trx_id,
                        acc_id=acc_id,
                        amount=dep_amt
                    ).to_dict()
                    self.data["transactions"].append(trx)

                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.WITHDRWAL.value:
                result = acc.withdraw()
                if isinstance(result, tuple):
                    exp_amt, category = result
                    if exp_amt and category:
                        trx_id = self.generate_id("trx", self.TRX)
                        trx = WithdrawalTrx(
                            id=trx_id,
                            category=category,
                            amount=exp_amt
                        ).to_dict()
                        self.data["transactions"].append(trx)

                state = AccDashState.ACC_DASH.value

            elif state == AccDashState.DEACTIVATE.value:
                state = acc.deactivate()

        return
        
    def list_transactions(self):
        """Displays a list of all transactions."""

        if not self.data["transactions"]:
            print("\n  [!] No transactions found in this ledger.\n")
            return

        print("\n  TRANSACTION HISTORY")
        print("  " + "—" * 45)
        print(f"  {'ID':<13} {'Type':<11} {'Amount':>16}")
        print("  " + "—" * 45)

        for trx in self.data["transactions"]:
            trx_id = trx['id']
            trx_type = trx['transaction_type'].capitalize()
            
            # Add clear structural visual signs for financial directions
            if trx['transaction_type'] == TrxType.DEPOSIT.value:
                amt_str = f"+${trx['amount']:,.2f}"
            else:
                amt_str = f"-${trx['amount']:,.2f}"

            print(f"  {trx_id:<13} {trx_type:<11} {amt_str:>16}")

        print("  " + "—" * 45 + "\n")

    def reports(self):
        """Displays a concise overview of user financial legder."""

        active_accs: list[Account] = [
            acc
            for acc in self.data["accounts"].values()
            if acc.acc_status == AccStat.ACTIVE.value
        ]

        net_balance = sum(acc.balance for acc in active_accs)

        total_income = sum(
            trx["amount"] 
            for trx in self.data["transactions"] 
            if trx["transaction_type"] == TrxType.DEPOSIT.value
        )

        total_expense = sum(
            trx["amount"] 
            for trx in self.data["transactions"] 
            if trx["transaction_type"] == TrxType.WITHDRAW.value
        )

        expense_category = {}
        for trx in self.data["transactions"]:
            if trx["transaction_type"] == TrxType.WITHDRAW.value:
                cat = trx["category"].title()
                expense_category[cat] = expense_category.get(cat, 0) + trx["amount"]

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

    def reactivate_acc(self):
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
                inactive_accs_map,
                "ACCOUNT REACTIVATION"
            )
        except InvalidOptionError as err:
            print(err)
            return

        acc = self.data["accounts"][inactive_acc_id]
        
        acc.reactivate()
        print(f"\n  [✓] Account '{acc.acc_name}' (ID: {acc.id}) has been successfully reactivated!\n")
    
    def save(self):
        """Saves tracker data"""
        save_tracker_data(self.data)

    def load(self):
        """Loads tracker data"""
        self.data = load_tracker_data()