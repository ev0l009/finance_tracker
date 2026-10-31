"""Unit tests for the Data Persistence storage engine.

Verifies folder initializations, file loading failures, data corruption recovery,
and atomic JSON serialization workflows within a mocked filesystem sandbox.
"""

import io
import json
import shutil
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from file_manager import storage
from models.account import Account
from models.types import TrackerData


class TestStorageSystem(unittest.TestCase):
    """Test suite verifying serialization, loading, and folder staging states."""

    def setUp(self) -> None:
        """Configures a sandboxed data environment path to insulate storage blocks."""
        self.test_dir = Path(__file__).resolve().parent / "test_sandbox_db"
        self.test_file = self.test_dir / "test_data.json"

        # Apply file resolution overrides across the target module environment
        self.dir_patcher = patch("file_manager.storage.DB_DIR", self.test_dir)
        self.file_patcher = patch("file_manager.storage.FILE_PATH", self.test_file)
        self.dir_patcher.start()
        self.file_patcher.start()

        # Initialize raw dataset templates mapping application mock records
        self.mock_account = Account(
            id="acc_SaM01",
            acc_name="Sandbox Fund",
            acc_type="cash",
            amount=3500,
            created_at=datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc),
        )
        self.tracker_payload: TrackerData = {
            "accounts": {"acc_SaM01": self.mock_account},
            "transactions": [
                {
                    "id": "trx_Wxl05",
                    "amount": 200,
                    "category": "bills",
                    "transaction_type": "withdraw",
                    "timestamp": datetime(2026, 10, 31, 12, 5, 0, tzinfo=timezone.utc),
                }
            ],
        }

    def tearDown(self) -> None:
        """Cleans up and completely wipes the temporary sandbox database folder."""
        self.dir_patcher.stop()
        self.file_patcher.stop()
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    # --- ATOMIC WRITE & CONFIGURATION TESTS ---

    def test_initialize_creates_directory_structure(self) -> None:
        """Confirms directory generation routines build necessary tree routes cleanly."""
        self.assertFalse(self.test_dir.exists())
        storage.initialize()
        self.assertTrue(self.test_dir.exists())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_save_tracker_data_serializes_atomically(self, mock_stdout) -> None:
        """Verifies objects convert into primitive structures and execute atomic write stages."""
        storage.save_tracker_data(self.tracker_payload)

        # Confirm the file target was populated on disk successfully
        self.assertTrue(self.test_file.exists())

        with open(self.test_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("acc_SaM01", data["accounts"])
        self.assertEqual(data["accounts"]["acc_SaM01"]["acc_name"], "Sandbox Fund")
        self.assertEqual(data["transactions"][0]["timestamp"], "2026-10-31T12:05:00+00:00")

    # --- EXCEPTION HANDLING & RECOVERY LAYER TESTS ---

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_tracker_data_missing_file_fallback(self, mock_stdout) -> None:
        """Ensures missing files cause safe default framework setups to build cleanly."""
        self.assertFalse(self.test_file.exists())
        loaded_data = storage.load_tracker_data()

        self.assertEqual(loaded_data["accounts"], {})
        self.assertEqual(loaded_data["transactions"], [])
        self.assertIn("No saved sessions found.", mock_stdout.getvalue())

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_load_tracker_data_corrupted_json_recovery(self, mock_stdout) -> None:
        """Verifies corrupted file formatting resets to empty tracking layouts gracefully."""
        storage.initialize()
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("{ INVALID MALFORMED STRUCTURAL JSON BLOB }")

        loaded_data = storage.load_tracker_data()
        self.assertEqual(loaded_data["accounts"], {})
        self.assertIn("Data file is corrupted.", mock_stdout.getvalue())

    # --- ROUND-TRIP HYDRATION TESTS ---

    def test_save_and_load_round_trip_hydration(self) -> None:
        """Ensures serialized maps recover correctly back into full live class definitions."""
        storage.save_tracker_data(self.tracker_payload)
        loaded_data = storage.load_tracker_data()

        # Extract recreated elements from the return payload
        recovered_acc = loaded_data["accounts"]["acc_SaM01"]
        recovered_trx = loaded_data["transactions"][0]

        # Assert full structural recovery properties match original types perfectly
        self.assertIsInstance(recovered_acc, Account)
        self.assertEqual(recovered_acc.acc_name, "Sandbox Fund")
        self.assertEqual(recovered_acc.balance, 3500)
        self.assertIsInstance(recovered_trx["timestamp"], datetime)


if __name__ == "__main__":
    unittest.main()
