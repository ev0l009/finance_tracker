"""Unit tests for the Data Persistence storage engine.

Verifies folder initializations, file loading failures, data corruption recovery, and atomic JSON serialization workflows within a mocked filesystem sandbox.
"""

import unittest
from pathlib import Path
from unittest.mock import patch
from file_manager import storage
from models.account import Account
from models.transaction import WithdrawalTrx
from models.types import AccType, TrackerData, TrxType
from datetime import datetime, timezone
import shutil
import json
import io

class TestStorageSystem(unittest.TestCase):
    def setUp(self) -> None:
        self.test_db_dir = Path(__file__).resolve().parent / "test_sandbox_dir"
        self.test_db_file = self.test_db_dir / "test_data_file.json"
        
        # 1. Clean up the folder after tests finish
        self.addCleanup(lambda: shutil.rmtree(self.test_db_dir) if self.test_db_dir.exists() else None)

        # 2. Patch the directory path
        self.dir_patcher = patch("file_manager.storage.DB_DIR", self.test_db_dir)
        self.dir_patcher.start()
        self.addCleanup(self.dir_patcher.stop)

        # 3. Patch the file path
        self.file_patcher = patch("file_manager.storage.FILE_PATH", self.test_db_file)
        self.file_patcher.start()
        self.addCleanup(self.file_patcher.stop)

        # Mock objects for testing
        self.mock_acc = Account(
            id="acc_abc12",
            acc_name="Test Acc",
            acc_type=AccType.BANK.value,
            amount=5000,
            created_at=datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.mock_trx = WithdrawalTrx(
            id="trx_456Ty",
            amount=2000,
            acc_id="acc_abc12",
            transaction_type=TrxType.WITHDRAW.value,
            category="others"
        )
        self.mock_data: TrackerData = {
            "accounts": { "acc_abc12": self.mock_acc },
            "transactions": [self.mock_trx]
        }

    def test_initialize_function(self):
        """Confirms directory generation routines build necessary tree routes cleanly."""
        self.assertFalse(self.test_db_dir.exists())
        storage.initialize()
        self.assertTrue(self.test_db_dir)

    def test_save_tracker_data(self):
        """Verifies objects convert into primitive structures and execute atomic write stages."""
        storage.save_tracker_data(self.mock_data)
        self.assertTrue(self.test_db_file.exists())

        with open(self.test_db_file, "r") as file:
            raw_test_data = json.load(file)

        self.assertTrue(raw_test_data["accounts"])
        self.assertTrue(raw_test_data["transactions"])
        self.assertTrue(raw_test_data["accounts"]["acc_abc12"])
        self.assertEqual(raw_test_data["accounts"]["acc_abc12"]["id"], "acc_abc12")
        self.assertEqual(raw_test_data["accounts"]["acc_abc12"]["acc_name"], "Test Acc")
        self.assertEqual(raw_test_data["accounts"]["acc_abc12"]["acc_type"], AccType.BANK.value)
        self.assertEqual(raw_test_data["accounts"]["acc_abc12"]["balance"], 5000)
        self.assertIsInstance(raw_test_data["accounts"]["acc_abc12"]["created_at"], str)

        self.assertTrue(raw_test_data["transactions"])
        self.assertEqual(raw_test_data["transactions"][0]["id"], "trx_456Ty")
        self.assertEqual(raw_test_data["transactions"][0]["amount"], 2000)
        self.assertEqual(raw_test_data["transactions"][0]["category"], "others")
        self.assertEqual(raw_test_data["transactions"][0]["transaction_type"], TrxType.WITHDRAW.value)
        self.assertEqual(raw_test_data["transactions"][0]["timestamp"], "2026-10-31T12:00:00+00:00")

    # --- EXCEPTION HANDLING & RECOVERY LAYER TESTS ---

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_tracker_data_missing_file_fallback(self, mock_stdout):    # type: ignore
        """Ensures missing files cause safe default framework setups to build cleanly."""
        self.assertFalse(self.test_db_file.exists())
        loaded_data = storage.load_tracker_data()

        self.assertEqual(loaded_data["accounts"], {})
        self.assertEqual(loaded_data["transactions"], [])
        self.assertIn("No saved sessions found. Initializing new ledger...", mock_stdout.getvalue())    # type: ignore

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_tracker_data_corrupted_data_recovery(self, mock_stdout):  # type: ignore
        """Verifies corrupted file formatting resets to empty tracking layouts gracefully."""
        storage.initialize()
        with open(self.test_db_file, "w", encoding="utf-8") as file:
            file.write("{ INVALID MALFORMED STRUCTURAL JSON BLOB }")

        loaded_data = storage.load_tracker_data()
        self.assertEqual(loaded_data["accounts"], {})
        self.assertEqual(loaded_data["transactions"], [])
        self.assertIn("Alert: Data file is corrupted.", mock_stdout.getvalue()) # type: ignore

    # --- ROUND-TRIP HYDRATION TESTS ---

    def test_save_and_load_roud_trip_hydration(self):
        """Ensures serialized maps recover correctly back into full live class definitions."""
        storage.save_tracker_data(self.mock_data)
        loaded_data = storage.load_tracker_data()

        test_acc = loaded_data["accounts"]["acc_abc12"]
        test_trx = loaded_data["transactions"][0]

        self.assertIsInstance(test_acc, Account)
        self.assertEqual(test_acc.id, "acc_abc12")
        self.assertEqual(test_acc.acc_name, "Test Acc")
        self.assertEqual(test_acc.acc_type, AccType.BANK.value)
        self.assertEqual(test_acc.balance, 5000)
        self.assertIsInstance(test_acc.created_at, datetime)

        self.assertEqual(test_trx.id, "trx_456Ty")
        self.assertEqual(test_trx.amount, 2000)
        self.assertEqual(test_trx.category, "others") # type: ignore
        self.assertEqual(test_trx.transaction_type, TrxType.WITHDRAW.value)
        self.assertIsInstance(test_trx.timestamp, datetime)

if __name__ == "__main__":
    unittest.main()