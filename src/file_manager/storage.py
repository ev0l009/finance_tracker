"""Data persistence layer for the Finance Tracker application.

Handles atomic serialization and deserialization of application data to and
from a JSON storage file, converting between live Python objects/datetimes 
and primitive JSON formats.
"""

from datetime import datetime
import json
import os
from pathlib import Path

from models.account import Account
from models.types import JsonTrackerData, TrackerData

# Resolution of relative project paths
DB_DIR = Path(__file__).resolve().parent.parent.parent / "db"
FILE_PATH = DB_DIR / "data.json"


def initialize() -> None:
    """Creates the database directory if it does not already exist."""
    DB_DIR.mkdir(exist_ok=True, parents=True)


def save_tracker_data(tracker_data: TrackerData) -> None:
    """Serializes in-memory tracker state and saves it atomically to a JSON file.

    Transforms Account objects into dictionaries and datetime objects into 
    ISO 8601 strings. Uses a temporary file staging technique to guarantee 
    file integrity.
    """
    serialized_data: JsonTrackerData = {
        "accounts": {},
        "transactions": []
    }

    # Transform live Account objects into plain dictionaries
    for acc_id, acc in tracker_data.get("accounts", {}).items():
        serialized_data["accounts"][acc_id] = acc.to_dict()

    # Normalize transaction timestamps to ISO strings
    for trx in tracker_data.get("transactions", []):
        trx_copy = trx.copy()
        timestamp = trx_copy.get("timestamp")
        
        if isinstance(timestamp, datetime):
            trx_copy["timestamp"] = timestamp.isoformat()
            
        serialized_data["transactions"].append(trx_copy)

    temp_file_path = FILE_PATH.with_suffix(".json.tmp")

    try:
        # Guarantee parent directory exists before attempting write
        initialize()
        
        with open(temp_file_path, "w", encoding="utf-8") as file:
            json.dump(serialized_data, file, indent=4)
            
        # Atomic replacement swaps temporary file to target filename
        os.replace(temp_file_path, FILE_PATH)
        print("\n  [✓] Session saved successfully.\n")

    except Exception as err:
        print(f"\n  [!] Error: Unable to save session. Details: {err}")
        if temp_file_path.exists():
            temp_file_path.unlink()


def load_tracker_data() -> TrackerData:
    """Loads and deserializes structural records from the primary JSON data file.

    Reconstructs Python datetime objects and parses stored dictionaries back 
    into standard Account model instances.

    Returns:
        TrackerData: An in-memory application dictionary populated with records.
    """
    deserialized_data: TrackerData = {
        "accounts": {},
        "transactions": []
    }

    try:
        with open(FILE_PATH, "r", encoding="utf-8") as file:
            raw_data = json.load(file)
            
    except FileNotFoundError:
        print("\n  [i] No saved sessions found. Initializing new ledger...")
        initialize()
        return deserialized_data

    except json.JSONDecodeError:
        print("\n  [!] Alert: Data file is corrupted. Initializing a clean session...\n")
        return deserialized_data

    except Exception as err:
        print(f"\n  [!] Unexpected error loading session: {err}")
        return deserialized_data

    # Hydrate raw dictionary records back into native Python types
    for acc_id, acc in raw_data.get("accounts", {}).items():
        acc_copy = acc.copy()
        created_at = acc_copy.get("created_at")

        if isinstance(created_at, str):
            acc_copy["created_at"] = datetime.fromisoformat(created_at)

        deserialized_data["accounts"][acc_id] = Account(
            acc_id,
            acc_copy["acc_name"],
            acc_copy["acc_type"],
            acc_copy["balance"],
            acc_copy["created_at"]
        )

    # Rehydrate transaction timestamps back to datetime objects
    for trx in raw_data.get("transactions", []):
        trx_copy = trx.copy()
        timestamp = trx_copy.get("timestamp")

        if isinstance(timestamp, str):
            trx_copy["timestamp"] = datetime.fromisoformat(timestamp)
            
        deserialized_data["transactions"].append(trx_copy)

    print("\n  [✓] Session data loaded successfully.")
    return deserialized_data