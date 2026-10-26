from models.types import MenuState, AccType

def get_dashboard_opt() -> str:
    options = {
        "1": MenuState.CREATE_ACCOUNT.value,
        "2": "list_accounts",
        "3": "transfer",
        "4": "account_dashboard",
        "5": "transactions",
        "6": "financial_overview",
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


def get_acc_dashboard_opt(acc_name: str) -> str:
    options = {
        "1": "check_balance",
        "2": "deposit",
        "3": "withdraw",
        "4": "deactivate",
        "5": "main_menu",
        "6": "exit"
    }

    print(f"\n  ACCOUNT: {acc_name.upper()}")
    print("  " + "—" * 20)
    print("  1. Check Balance")
    print("  2. Deposit")
    print("  3. Withdraw")
    print("  4. Deactivate Account")
    print("  5. Main Menu")
    print("  6. Exit\n")

    choice = input("  Select option (1-6) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return "account_dashboard"

    return options[choice]



def get_account_type() -> str:
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
        raise ValueError("\n  [!] Invalid account type. Please try again.")

    return options[choice]
