from models.types import MenuState
from ui import get_dashboard_opt
from models.tracker import Tracker

def tracker_runner():
    tracker = Tracker()
    state = MenuState.DASHBOARD.value

    while state != MenuState.EXIT.value:
        if state == MenuState.DASHBOARD.value:
            state = get_dashboard_opt()

        elif state == MenuState.CREATE_ACCOUNT.value:
            tracker.create_account()
            state = MenuState.DASHBOARD.value
    
    print("\nSaving session\n")
    print("Exiting")

tracker_runner()