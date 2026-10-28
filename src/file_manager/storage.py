from pathlib import Path
import json
from models.types import TrackerData
from datetime import datetime
from models.types import TrackerData, JsonTrackerData
from models.account import Account
import os

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
        serialized_data["accounts"][acc_id] = acc.to_dict()

    for trx in tracker_data.get("transactions", []):
        trx_copy = trx.copy()

        if "timestamp" in trx_copy and trx_copy["timestamp"]:
            trx_copy["timestamp"] = trx_copy["timestamp"].isoformat() if isinstance(trx_copy["timestamp"], datetime) else trx_copy["timestamp"]

        serialized_data["transactions"].append(trx_copy)

    temp_file_path = f"{FILE_PATH}.tmp"

    try:
        with open(temp_file_path, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except FileNotFoundError:
        print("\n  [i] Database file not found. Initializing new ledger...")
        initialize()
        with open(FILE_PATH, "w") as file:
            json.dump(serialized_data, file, indent=4)
    except Exception as err:
        print(f"\n  [!] Error: Unable to save session. Details: {err}")
    else:
        os.replace(temp_file_path, FILE_PATH)
        print("\n  [✓] Session saved successfully.\n")

def load_tracker_data() ->TrackerData:
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
                    datetime.fromisoformat(acc_copy["created_at"])
                    if isinstance(acc_copy["created_at"], str)
                    else acc_copy["created_at"]
                )
        
            deserialized_data["accounts"][acc_id] = Account(
                acc_id,
                acc_copy["acc_name"],
                acc_copy["acc_type"],
                acc_copy["balance"],
                acc_copy["created_at"]
            )

        for trx in raw_data.get("transactions", []):
            trx_copy = trx.copy()

            if "timestamp" in trx_copy and trx_copy["timestamp"]:
                trx_copy["timestamp"] = datetime.fromisoformat(
                    trx_copy["timestamp"]) if isinstance(trx_copy["timestamp"], str) else trx_copy["timestamp"]
            
            deserialized_data["transactions"].append(trx_copy)

    print("\n  [✓] Session data loaded successfully.\n")
    return deserialized_data