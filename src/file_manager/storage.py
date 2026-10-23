from pathlib import Path
from models.types import TrackerData
import json
from datetime import datetime

DB_DIR = Path(__file__).resolve().parent.parent.parent/"data"
FILE_PATH = DB_DIR/"data.json"

def initialize_storage():
        DB_DIR.mkdir(parents=True, exist_ok=True)

def save_session(data: TrackerData):
    try:
        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
    except FileNotFoundError:
        print(
            "\nCouldn't find any previously saved sessions\n"
            "Creating new database\n"
        )
        initialize_storage()
        with open(FILE_PATH, "w") as file:
            json.dump(data, file, indent=4)
        print("\nSession saved successfully.")
    except json.JSONDecodeError as err:
         print(f"\nErr: {err}")
    else:
         print("\nSession saved successfully.")

# def load_session():
#     if not FILE_PATH:
#          initialize_storage()

#     deserialized_data: TrackerData = {
#         "accounts": {},
#         "transactions": []
#     }

#     try:
#         with open(FILE_PATH, "r") as file:
#             raw_data: TrackerData = json.load(file)
#     except (json.JSONDecodeError, FileNotFoundError, PermissionError) as err:
#         print(f"\nErr while loading file: {err}")

#     # Deserialize Accounts
#     for acc_id, acc in raw_data.get("accounts", {}).items():
#         # Copy the dictionary to avoid mutating the raw data
#         account_copy = acc.copy()

#         # Convert the ISO timestamp string back to a datetime object
#         if "created_at" in account_copy and account_copy["created_at"]:
#             account_copy["created_at"] = datetime.fromisoformat(account_copy["created_at"])


def load_session() -> TrackerData:
    deserialized_data: TrackerData = {
        "accounts": {},
        "transactions": []
    }

    try:
        with open(FILE_PATH, "r") as file:
            raw_data: TrackerData = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError) as err:
        print(f"\nErr while loading file: {err}")
        return deserialized_data  # Return empty structure if file read fails

    # Deserialize Accounts
    for acc_id, acc in raw_data.get("accounts", {}).items():
        # Copy the dictionary to avoid mutating the raw data
        account_copy = acc.copy()
        
        # Convert the ISO timestamp string back to a datetime object
        if "created_at" in account_copy and account_copy["created_at"]:
            account_copy["created_at"] = datetime.fromisoformat(account_copy["created_at"])
            
        deserialized_data["accounts"][acc_id] = account_copy

    # Deserialize Transactions (assuming they also have timestamps)
    for tx in raw_data.get("transactions", []):
        tx_copy = tx.copy()
        if "created_at" in tx_copy and tx_copy["created_at"]:
            tx_copy["created_at"] = datetime.fromisoformat(tx_copy["created_at"])
        deserialized_data["transactions"].append(tx_copy)

    return deserialized_data