"""Unit tests for the Account domain model.

Verifies financial invariants, lifecycle status restrictions, and safety boundaries
governing credits, debits, and account configurations.
"""

import unittest
from datetime import datetime
from models.account import Account


class TestAccountInvariants(unittest.TestCase):
    """Test suite ensuring Account core data invariants remain protected."""

    def setUp(self) -> None:
        """Initializes a pristine Account instance before each test run."""
        self.sample_account = Account(
            id="acc_Tst12",
            acc_name="Test Checking",
            acc_type="bank",
            amount=50000,  # Stored as an integer ($500.00 equivalent)
        )

    def test_account_initialization_safety(self) -> None:
        """Ensures core properties assign correctly and protect write-once invariants."""
        self.assertEqual(self.sample_account.id, "acc_Tst12")
        self.assertEqual(self.sample_account.acc_name, "Test Checking")
        self.assertEqual(self.sample_account.balance, 50000)
        self.assertIsInstance(self.sample_account.created_at, datetime)

        # Verify read-only properties throw errors if mutation is attempted
        with self.assertRaises(AttributeError):
            self.sample_account.id = "new_id"  # type: ignore

    def test_invalid_initialization_raises_value_error(self) -> None:
        """Verifies that bad configuration arguments crash safely on instantiation."""
        # Empty IDs are blocked
        with self.assertRaises(ValueError):
            Account(id=" ", acc_name="Bad Acc", acc_type="bank", amount=1000)

        # Unrecognized account types are blocked
        with self.assertRaises(ValueError):
            Account(id="acc_1", acc_name="Bad Acc", acc_type="crypto", amount=1000)

    def test_credit_increases_balance_correctly(self) -> None:
        """Verifies credit transactions increment available balances cleanly."""
        self.sample_account.credit(15000)
        self.assertEqual(self.sample_account.balance, 65000)

    def test_debit_decreases_balance_correctly(self) -> None:
        """Verifies debit transactions decrement available balances cleanly."""
        self.sample_account.debit(20000)
        self.assertEqual(self.sample_account.balance, 30000)

    def test_negative_balance_invariant_enforcement(self) -> None:
        """Guarantees balances can never be forced beneath zero."""
        # Debiting more than available assets should raise a ValueError
        with self.assertRaises(ValueError):
            self.sample_account.debit(60000)

        # Setting property balance beneath zero directly should raise a ValueError
        with self.assertRaises(ValueError):
            self.sample_account.balance = -100

    def test_inactive_account_locks_transactions(self) -> None:
        """Verifies that locking/deactivating an account blocks credits and debits."""
        self.sample_account.acc_status = "inactive"

        # Credits must be rejected on inactive files
        with self.assertRaises(PermissionError):
            self.sample_account.credit(5000)

        # Debits must be rejected on inactive files
        with self.assertRaises(PermissionError):
            self.sample_account.debit(5000)

    def test_conditional_deactivation_rules(self) -> None:
        """Ensures an account can only be deactivated if its balance is exactly zero."""
        # Balance is currently 50000 -> Should fail deactivation
        can_deactivate = self.sample_account.deactivate_account()
        self.assertFalse(can_deactivate)
        self.assertEqual(self.sample_account.acc_status, "active")

        # Empty the balance out
        self.sample_account.debit(50000)
        
        # Balance is now 0 -> Should successfully deactivate
        can_deactivate_now = self.sample_account.deactivate_account()
        self.assertTrue(can_deactivate_now)
        self.assertEqual(self.sample_account.acc_status, "inactive")


if __name__ == "__main__":
    unittest.main()
