from pathlib import Path
import json
from models.types import TrackerData
from datetime import datetime
from models.types import TrackerData

DB_DIR = Path(__file__).resolve().parent.parent.parent/"db"
FILE_PATH = DB_DIR/"data.json"

def initialize():
    DB_DIR.mkdir(exist_ok=True, parents=True)

def save_tracker_data(tracker_data: TrackerData):
    serialized_data:  TrackerData = {
        "accounts": {},
        "transactions": []
    }

    for acc_id, acc in tracker_data.get("accounts", {}).items():
        acc_copy = acc.copy()

        if "created_at" in acc_copy and acc_copy["created_at"]:
            acc_copy["created_at"] = (
                acc_copy["created_at"].strftime("%Y:%m:%d %H:%M:%S")
                if isinstance(acc_copy["created_at"], datetime)
                else acc_copy["created_at"]
            )
        
        serialized_data["accounts"][acc_id] = acc_copy

    try:
        with open(FILE_PATH, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except FileNotFoundError:
        print("\nDB File not found. Initializing file...")
        initialize()
        with open(FILE_PATH, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except Exception as err:
        print(f"Couldn't save your session: {err}")
    else:
        print("\nSession saved successfully\n")

def load_tracker_data():
    deserialized_data: TrackerData = {
        "accounts": {},
        "transactions": []
    }

    try:
        with open(FILE_PATH, "r") as file:
            raw_data = json.load(file)
    except FileNotFoundError:
        print("\nCouldn't find any saved sessions. Initializing new session")
        initialize()
        return deserialized_data

    except json.JSONDecodeError:
        print("\nData has been corrupted. Initializing a new session...\n")
        return deserialized_data

    except Exception as err:
        print(f"Err: {err}")
        return deserialized_data

    else:
        for acc_id, acc in raw_data.get("accounts", {}).items():
            acc_copy = acc.copy()

            if "created_at" in acc_copy and acc_copy["created_at"]:
                acc_copy["created_at"] = (
                    datetime.strptime(
                        acc_copy["created_at"], 
                        "%Y:%m:%d %H:%M:%S"
                    )
                    if isinstance(acc_copy["created_at"], str)
                    else acc_copy["created_at"]
                )
        
            deserialized_data["accounts"][acc_id] = acc_copy
    
    print("\nData loaded successfully.\n")
    return deserialized_data