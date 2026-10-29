"""User interface presentation layer for the Finance Tracker application.

Handles rendering menus, formatting text blocks, capturing terminal inputs,
and routing selections cleanly back into application state flows.
"""

from exceptions import InvalidOptionError, NullEligibleAccountsError
from models.types import AccDashState, AccType, MenuState


def get_dashboard_opt() -> str:
    """Displays the main menu interface and captures the next navigation state.

    Returns:
        str: The string value mapping to the next target MenuState.
    """
    options = {
        "1": MenuState.CREATE_ACCOUNT.value,
        "2": MenuState.LIST_ACCOUNTS.value,
        "3": MenuState.TRANSFER.value,
        "4": MenuState.ACC_DASHBOARD.value,
        "5": MenuState.TRANSACTIONS.value,
        "6": MenuState.REACTIVATE_ACC.value,
        "7": MenuState.REPORTS.value,
        "8": MenuState.EXIT.value,
    }

    print("\n  FINANCE TRACKER")
    print("  " + "—" * 20)
    print("  1. Create Account")
    print("  2. List Accounts")
    print("  3. Transfer Funds")
    print("  4. Inspect Account")
    print("  5. Transactions")
    print("  6. Reactivate Account")
    print("  7. Reports")
    print("  8. Exit\n")

    choice = input("  Select option (1-8) → ").strip()

    if choice not in options:
        print("  Invalid selection. Try again...")
        return MenuState.DASHBOARD.value

    return options[choice]


def get_acc_dash_state(acc_name: str) -> str:
    """Displays the individual account inspection actions sub-menu.

    Args:
        acc_name: The descriptive string name of the account under inspection.

    Returns:
        str: The string value mapping to the next target AccDashState.
    """
    options = {
        "1": AccDashState.BALANCE.value,
        "2": AccDashState.DEPOSIT.value,
        "3": AccDashState.WITHRAWAL.value,
        "4": AccDashState.DEACTIVATE.value,
        "5": AccDashState.RETURN.value,
    }

    print(f"\n  ACCOUNT: {acc_name.upper()}")
    print("  " + "—" * 20)
    print("  1. Check Balance")
    print("  2. Deposit")
    print("  3. Withdraw")
    print("  4. Deactivate Account")
    print("  5. Main Menu\n")

    choice = input("  Select option (1-5) → ").strip()

    if choice not in options:
        print("\n  [!] Invalid choice. Please try again.")
        return AccDashState.ACC_DASH.value

    return options[choice]


def get_account_type() -> str:
    """Prompts the user to select a valid system account classification type.

    Returns:
        str: The chosen primitive raw string value of the valid AccType.

    Raises:
        InvalidOptionError: If the input choice does not map to any account type.
    """
    options = {
        "1": AccType.BANK.value,
        "2": AccType.CASH.value,
        "3": AccType.SAVINGS.value,
        "4": AccType.MOBILE.value,
    }

    print("\n  Select account type:")
    print("  1. Bank")
    print("  2. Cash")
    print("  3. Savings")
    print("  4. Mobile Money\n")

    choice = input("  Select option (1-4) → ").strip()

    if choice not in options:
        raise InvalidOptionError("Invalid account type selection.")

    return options[choice]


def select_acc(
    acc_map: dict[str, str],
    id_to_skip: str | None = None,
    heading: str | None = None,
) -> str:
    """Renders a dynamically numbered list of accounts for user selection.

    Args:
        acc_map: Mapping containing structural database account IDs to names.
        id_to_skip: Optional ID constraint to omit from selection views.
        heading: Custom optional title overlay text for the selection layout.

    Returns:
        str: The unique account identity identifier string.

    Raises:
        NullEligibleAccountsError: If no valid accounts exist after filtering.
        InvalidOptionError: If user selections do not match active runtime keys.
    """
    options: dict[str, str] = {}
    title_text = heading.upper() if heading else "SELECT ACCOUNT"

    print(f"\n  {title_text}")
    print("  " + "—" * 25)

    idx = 1
    for acc_id, acc_name in acc_map.items():
        if acc_id == id_to_skip:
            continue
        print(f"  {idx}. {acc_name.title()}")
        options[str(idx)] = acc_id
        idx += 1

    if not options:
        raise NullEligibleAccountsError("No eligible accounts available.")

    print()
    choice = input(f"  Select option (1-{len(options)}) → ").strip()

    if choice not in options:
        raise InvalidOptionError("Invalid account selection. Selection canceled.")

    return options[choice]


def get_category() -> str:
    """Presents recognized expense categorization options for tracking.

    Returns:
        str: The chosen plain lowercase expense category label.

    Raises:
        InvalidOptionError: If the user provides an out-of-bounds input.
    """
    cat_options = {
        "1": "food",
        "2": "bills",
        "3": "transport",
        "4": "airtime",
        "5": "health",
        "6": "shopping",
        "7": "entertainment",
        "8": "others",
    }

    print("\n  Select category:")
    for idx, cat in cat_options.items():
        print(f"  {idx}. {cat.capitalize()}")

    print()
    choice = input(f"  Select option (1-{len(cat_options)}) → ").strip()

    if choice not in cat_options:
        raise InvalidOptionError("Invalid category selection. Selection canceled.")

    return cat_options[choice]