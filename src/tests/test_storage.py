import unittest
from pathlib import Path
from unittest.mock import patch
from file_manager import storage
from models.account import Account
from models.types import AccType, TrackerData, TrxType
from datetime import datetime, timezone
import shutil
import json

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
        self.mock_data: TrackerData = {
            "accounts": { "acc_abc12": self.mock_acc },
            "transactions": [
                {
                    "id": "trx_456Ty",
                    "amount": 2000,
                    "category": "others",
                    "transaction_type": TrxType.WITHDRAW.value,
                    "timestamp": datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc),
                }
            ]
        }

    def test_initialize_function(self):
        self.assertFalse(self.test_db_dir.exists())
        storage.initialize()
        self.assertTrue(self.test_db_dir)

    def test_save_tracker_data(self):
        storage.save_tracker_data(self.mock_data)
        self.assertTrue(self.test_db_file.exists())

        with open(self.test_db_file, "r") as file:
            raw_test_data = json.load(file)

        self.assertTrue(raw_test_data["accounts"])
        self.assertTrue(raw_test_data["transactions"])
        self.assertTrue(raw_test_data["accounts"]["trx_456Ty"])
        self.assertEqual(raw_test_data["accounts"]["trx_456Ty"]["id"], "acc_abc12")
        self.assertEqual(raw_test_data["accounts"]["trx_456Ty"]["acc_name"], "Test Acc")
        self.assertEqual(raw_test_data["accounts"]["trx_456Ty"]["acc_type"], AccType.BANK.value)
        self.assertEqual(raw_test_data["accounts"]["trx_456Ty"]["amount"], 5000)
        self.assertIsInstance(raw_test_data["accounts"]["trx_456Ty"]["created_at"], str)
        self.assertEqual(raw_test_data["accounts"]["trx_456Ty"]["created_at"], "2026-10-31T12:05:00+00:00")