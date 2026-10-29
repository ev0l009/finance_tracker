"""Displays menu user interfaces, collect user input an handles validation."""

from models.types import MenuState, AccType, AccDashState

from exceptions import InvalidOptionError, NullEligibleAccountsError

def get_dashboard_opt() -> str:
    """Displays main menu interface, collects user input returns a string that updates menu state
    
    Returns returns valid menu state."""
    options = {
        "1": MenuState.CREATE_ACCOUNT.value,
        "2": MenuState.LIST_ACCOUNTS.value,
        "3": MenuState.TRANSFER.value,
        "4": MenuState.ACC_DASHBOARD.value,
        "5": MenuState.TRANSACTIONS.value,
        "6": MenuState.REPORTS.value,
        "7": MenuState.EXIT.value
    }
 
    print("\n  FINANCE TRACKER")
    print("  " + "—" * 20)
    print("  1. Create Account")
    print("  2. List Accounts")
    print("  3. Transfer Funds")
    print("  4. Inspect Account")
    print("  5. Transactions")
    print("  6. Reports")
    print("  7. Exit\n")
    
    choice = input("  Select option (1-7) → ").strip()

    if choice not in options:
        print("  Invalid selection. Try again...")
        return MenuState.DASHBOARD.value

    return options[choice]


def get_acc_dash_state(acc_name: str) -> str:
    """Displays account dashboard menu, collects user input and returns a string that updates account menu state
    
    Returns returns valid account menu state."""
    options = {
        "1": AccDashState.BALANCE.value,
        "2": AccDashState.DEPOSIT.value,
        "3": AccDashState.WITHDRWAL.value,
        "4": AccDashState.DEACTIVATE.value,
        "5": AccDashState.RETURN.value
    }

    print(f"\n  ACCOUNT: {acc_name.upper()}")
    print("  " + "—" * 20)
    print("  1. Check Balance")
    print("  2. Deposit")
    print("  3. Withdraw")
    print("  4. Deactivate Account")
    print("  5. Main Menu\n")

    choice = input("  Select option (1-6) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return AccDashState.ACC_DASH.value

    return options[choice]


def get_account_type() -> str:
    """Displays valid account types and returns selected options as string.  
    
    Returns a valid account type.   
    
    ### Raises: 
        - `InvalidOptionError` - selected option is invalid"""
    options = {
        "1": AccType.BANK.value,
        "2": AccType.CASH.value,
        "3": AccType.SAVINGS.value,
        "4": AccType.MOBILE.value
    }

    print("\n  Select account type:")
    print("  1. Bank")
    print("  2. Cash")
    print("  3. Savings")
    print("  4. Mobile Money\n")

    choice = input("  Select option (1-4) → ").strip()

    if choice not in options:
        raise InvalidOptionError("\n  [!] Invalid account type. Please try again.")

    return options[choice]

def select_acc(
    acc_map: dict[str, str], 
    id_to_skip: str | None = None,
    heading: str | None = None
) -> str:
    """Displays a list for accounts for user selection and returns the account id.  
      
    ### Args:
        - acc_map `dict[str, str]`: a dictionary of account ids to account names.
        - id_to_skip `str`: account id to skip.
        - heading `str`: context specific heading for better UX.  
    
    Returns selected account id as string.
    
    ### Raises:
        - `InvalidOptionError` - selected option is invalid
        - `NullEligibleAccountsError` - no eligible accounts"""

    options: dict[str, str] = {}
    
    title_text = heading.upper() if heading else "SELECT ACCOUNT"
    print(f"\n  {title_text}")
    print("  " + "—" * 25)

    idx = 1
    for acc_id in acc_map:
        if acc_id == id_to_skip:
            continue
        print(f"  {idx}. {acc_map[acc_id].title()}")
        options[str(idx)] = acc_id
        idx += 1

    if not options:
        raise NullEligibleAccountsError("\n  [!] No eligible accounts available.\n")

    print()
    choice = input(f"  Select option (1-{len(options)}) → ").strip()

    if choice not in options:
        raise InvalidOptionError("\n  [!] Invalid account selection. Selection canceled.\n")

    return options[choice]

def get_category() -> str:
    """Displays a list of valid expenses categories.   
    
    Returns selected account id as string.
    
    ### Raises:
        - `InvalidOptionError` - selected option is invalid"""
    cat_options = {
        "1" : "food",
        "2" : "bills",
        "3" : "transport",
        "4" : "airtime",
        "5" : "health",
        "6" : "shopping",
        "7" : "entertainment",
        "8" : "other"
    }

    print("Select category: ")

    for idx, cat in cat_options.items():
        print(f"{idx}. {cat.capitalize()}")

    print()
    choice = input(f"  Select option (1-{len(cat_options)}) → ").strip()

    if choice not in cat_options:
        raise InvalidOptionError("\n  [!] Invalid category selection. Selection canceled.\n")

    return cat_options[choice]