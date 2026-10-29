"""Main entry point for the Finance Tracker application.

This module handles the main application lifecycle, state transitions, 
and user interface routing using a simplified State Pattern.
"""

from models.tracker import Tracker
from models.types import MenuState
from ui import get_dashboard_opt


def tracker_runner() -> None:
    """Runs the core application loop and manages menu state transitions.

    Initializes the system tracker, loads existing user data, routes the user 
    to the correct application screen based on the current state, and saves 
    all data securely upon exiting.
    """
    tracker = Tracker()
    tracker.load()

    # Initialise the loop with the main dashboard state
    current_state = MenuState.DASHBOARD.value

    # Core Application Loop
    while current_state != MenuState.EXIT.value:
        
        if current_state == MenuState.DASHBOARD.value:
            current_state = get_dashboard_opt()

        elif current_state == MenuState.CREATE_ACCOUNT.value:
            tracker.create_account()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.LIST_ACCOUNTS.value:
            tracker.list_accounts()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.TRANSFER.value:
            tracker.transfer()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.ACC_DASHBOARD.value:
            tracker.acc_dashboard()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.REACTIVATE_ACC.value:
            tracker.reactivate_acc()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.TRANSACTIONS.value:
            tracker.list_transactions()
            current_state = MenuState.DASHBOARD.value

        elif current_state == MenuState.REPORTS.value:
            tracker.reports()
            current_state = MenuState.DASHBOARD.value
    
    # Clean up and data persistence on exit
    tracker.save()
    print("  • Exiting system...")


if __name__ == "__main__":
    tracker_runner()
