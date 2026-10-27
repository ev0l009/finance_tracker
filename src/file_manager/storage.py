from pathlib import Path
import json
from models.types import TrackerData
from datetime import datetime
from models.types import TrackerData, JsonTrackerData

DB_DIR = Path(__file__).resolve().parent.parent.parent/"db"
FILE_PATH = DB_DIR/"data.json"

def initialize():
    DB_DIR.mkdir(exist_ok=True, parents=True)

def save_tracker_data(tracker_data: TrackerData):
    serialized_data:  JsonTrackerData = {
        "accounts": {},
        "transactions": []
    }

    for acc_id, acc in tracker_data.get("accounts", {}).items():
        if acc.created_at:
            acc.created_at.strftime("%Y:%m:%d %H:%M:%S")
        
        serialized_data["accounts"][acc_id] = acc.to_dict()

    for trx in tracker_data.get("transactions", []):
        trx_copy = trx.copy()

        if "timestamp" in trx_copy and trx_copy["timestamp"]:
            trx_copy["timestamp"] = trx_copy["timestamp"].strftime("%Y:%m:%d %H:%M:%S") if isinstance(trx_copy["timestamp"], datetime) else trx_copy["timestamp"]

        serialized_data["transactions"].append(trx_copy)


    try:
        with open(FILE_PATH, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except FileNotFoundError:
        print("\n  [i] Database file not found. Initializing new ledger...")
        initialize()
        with open(FILE_PATH, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except Exception as err:
        print(f"\n  [!] Error: Unable to save session. Details: {err}")
    else:
        print("\n  [✓] Session saved successfully.\n")

def load_tracker_data():
    deserialized_data: TrackerData = {
        "accounts": {},
        "transactions": []
    }

    try:
        with open(FILE_PATH, "r") as file:
            raw_data = json.load(file)
    except FileNotFoundError:
        print("\n  [i] No saved sessions found. Initializing new ledger...")
        initialize()
        return deserialized_data

    except json.JSONDecodeError:
        print("\n  [!] Alert: Data file is corrupted. Initializing a clean session...\n")
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

        for trx in deserialized_data.get("transactions", []):
            trx_copy = trx.copy()

            if "timestamp" in trx_copy and trx_copy["timestamp"]:
                trx_copy["timestamp"] = datetime.strptime(
                    trx_copy["timestamp"], 
                    "%Y:%m%d %H:%M:%S") if isinstance(trx_copy["timestamp"], str) else trx_copy["timestamp"]
            
            deserialized_data["transactions"].append(trx_copy)
            
    print("\n  [✓] Session data loaded successfully.\n")
    return deserialized_data