"""Unit tests for the Tracker core orchestration engine.

Verifies non-colliding ID generation, account initialization pipelines, 
cross-account transfer validation rules, financial reporting aggregates, 
and state synchronization flows.
"""

import io
import unittest
from unittest.mock import patch

from models.account import Account
from models.tracker import Tracker
from models.types import TrxType


class TestTrackerOrchestration(unittest.TestCase):
    """Test suite ensuring master orchestration routines preserve data safety rules."""

    def setUp(self) -> None:
        """Initializes a fresh Tracker engine instance before each test run."""
        self.tracker = Tracker()

        # Inject two pre-configured active accounts for transaction and transfer testing
        self.acc1_id = "acc_aaaaa"
        self.acc2_id = "acc_bbbbb"
        
        self.tracker.data["accounts"][self.acc1_id] = Account(
            id=self.acc1_id, acc_name="Primary Checking", acc_type="bank", amount=50000
        )
        self.tracker.data["accounts"][self.acc2_id] = Account(
            id=self.acc2_id, acc_name="Emergency Cash", acc_type="cash", amount=10000
        )

    # --- IDENTIFIER DEDUPLICATION LAYER TESTS ---

    def test_generate_id_is_unique_and_formatted(self) -> None:
        """Ensures generated IDs conform to size expectations and do not cause collisions."""
        gen_id = self.tracker.generate_id("acc", Tracker.ACC)
        
        self.assertTrue(gen_id.startswith("acc_"))
        self.assertEqual(len(gen_id), 9)  # 3 (prefix) + 1 (_) + 5 (suffix)

        # Force a simulated duplicate scenario to verify loop safety
        self.tracker.data["accounts"]["acc_dupe1"] = Account(
            id="acc_dupe1", acc_name="Dupe", acc_type="cash", amount=0
        )
        
        with patch("secrets.choice", side_with_sequence=["d", "u", "p", "e", "1", "x", "y", "z", "w", "v"]):
            # First suffix choice will collide with 'dupe1', forcing the tracker loop to refresh
            new_id = self.tracker.generate_id("acc", Tracker.ACC)
            self.assertNotEqual(new_id, "acc_dupe1")

    # --- ACCOUNT CREATION CONTROL PIPELINE TESTS ---

    @patch("builtins.input", side_effect=["Investment Fund", "10000"])
    @patch("models.tracker.get_account_type", return_value="savings")
    def test_create_account_happy_path(self, mock_acc_type, mock_input) -> None:
        """Verifies account creation workflow registers objects and logs funding events."""
        # Confirm starting counts
        self.assertEqual(len(self.tracker.data["accounts"]), 2)
        
        self.tracker.create_account()
        
        # Verify changes updated our engine memory maps cleanly
        self.assertEqual(len(self.tracker.data["accounts"]), 3)
        
        # Ensure a funding transaction entry was automatically logged for the opening balance
        self.assertEqual(len(self.tracker.data["transactions"]), 1)
        self.assertEqual(self.tracker.data["transactions"][0]["amount"], 10000)
        self.assertEqual(self.tracker.data["transactions"][0]["transaction_type"], TrxType.DEPOSIT.value)

    # --- INTER-ACCOUNT FUND TRANSFER TESTS ---

    @patch("builtins.input", return_value="15000")
    @patch("models.tracker.select_acc", side_effect=["acc_aaaaa", "acc_bbbbb"])
    def test_transfer_funds_successful_execution(self, mock_select_acc, mock_input) -> None:
        """Confirms transfer channels safely decrement sources and increment targets."""
        sender = self.tracker.data["accounts"][self.acc1_id]
        receiver = self.tracker.data["accounts"][self.acc2_id]

        self.tracker.transfer()

        # Balance validations ($500 -> $350 and $100 -> $250)
        self.assertEqual(sender.balance, 35000)
        self.assertEqual(receiver.balance, 25000)

        # Audit ledger log checks
        self.assertEqual(len(self.tracker.data["transactions"]), 1)
        self.assertEqual(self.tracker.data["transactions"][0]["transaction_type"], TrxType.TRANSFER.value)
        self.assertEqual(self.tracker.data["transactions"][0]["source_acc_id"], self.acc1_id)
        self.assertEqual(self.tracker.data["transactions"][0]["target_acc_id"], self.acc2_id)

    @patch("builtins.input", return_value="60000")  # Overdraft attempt
    @patch("models.tracker.select_acc", return_value="acc_aaaaa")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_transfer_insufficient_funds_aborts(self, mock_stdout, mock_select_acc, mock_input) -> None:
        """Guarantees transfer actions terminate early if balances are insufficient."""
        self.tracker.transfer()
        
        # Invariant checks: balances must remain unchanged
        self.assertEqual(self.tracker.data["accounts"][self.acc1_id].balance, 50000)
        self.assertIn("Insufficient available funds", mock_stdout.getvalue())

    # --- ANALYTICAL FINANCIAL REPORT TESTS ---

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_reports_aggregates_metrics_correctly(self, mock_stdout) -> None:
        """Verifies report calculation routines aggregate global metrics transparently."""
        # Seed explicit mock transactions to feed aggregation filters
        self.tracker.data["transactions"].extend([
            {"id": "t1", "amount": 5000, "transaction_type": TrxType.DEPOSIT.value},
            {"id": "t2", "amount": 1200, "transaction_type": TrxType.WITHDRAW.value, "category": "Food"},
            {"id": "t3", "amount": 800, "transaction_type": TrxType.WITHDRAW.value, "category": "Bills"}
        ])

        self.tracker.reports()
        output = mock_stdout.getvalue()

        # Verify macro analytics are calculated and displayed correctly
        self.assertIn("Net Total Balance:  $600.00", output)  # 50000 + 10000
        self.assertIn("Total Income (+):   $50.00", output)   # 5000
        self.assertIn("Total Expenses (-): $20.00", output)   # 1200 + 800
        self.assertIn("Food               $12.00", output)

    # --- PERSISTENCE SYNCHRONIZATION ROUTINE TESTS ---

    @patch("models.tracker.save_tracker_data")
    @patch("models.tracker.load_tracker_data")
    def test_save_and_load_invoke_storage_layer(self, mock_load, mock_save) -> None:
        """Confirms engine save/load commands cleanly call downstream file storage pipelines."""
        self.tracker.save()
        mock_save.assert_called_once_with(self.tracker.data)

        self.tracker.load()
        mock_load.assert_called_once()


if __name__ == "__main__":
    unittest.main()
