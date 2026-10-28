# I opted for a state pattern machine for the app flow. It's pretty direct and concise.

"""Main entry point to app."""
# To get required menu states
from models.types import MenuState
# To update menu state
from ui import get_dashboard_opt
# to initialize tracker object
from models.tracker import Tracker

def tracker_runner():
    """Runs the finance tracker menu loop"""

    tracker = Tracker()

    # Default menu state to display menu when program runs
    state = MenuState.DASHBOARD.value

    # To load tracker data
    tracker.load()

    # App/Menu loop
    while state != MenuState.EXIT.value:
        if state == MenuState.DASHBOARD.value:
            state = get_dashboard_opt()

        elif state == MenuState.CREATE_ACCOUNT.value:
            tracker.create_account()
            state = MenuState.DASHBOARD.value

        elif state == MenuState.LIST_ACCOUNTS.value:
            tracker.list_accounts()
            state = MenuState.DASHBOARD.value

        elif state == MenuState.TRANSFER.value:
            tracker.transfer()
            state = MenuState.DASHBOARD.value

        elif state == MenuState.ACC_DASHBOARD.value:
            tracker.acc_dashboard()
            state = MenuState.DASHBOARD.value

        elif state == MenuState.TRANSACTIONS.value:
            tracker.list_transactions()
            state = MenuState.DASHBOARD.value

        elif state == MenuState.REPORTS.value:
            tracker.reports()
            state = MenuState.DASHBOARD.value
    
    # To save tracker data as program closes.
    tracker.save()
    print("  • Exiting system...")
 
tracker_runner()