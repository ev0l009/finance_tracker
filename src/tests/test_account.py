"""Unit tests for the Account domain model.

Verifies financial invariants, lifecycle status restrictions, and safety boundaries
governing credits, debits, and account configurations.
"""

import unittest
from models.account import Account
from models.types import AccType, AccStat
from datetime import datetime
from exceptions import AccNameError, InvalidIDError, InvalidAccountTypeError, InvalidAmountError, ExcessDebitError, AccStatusError, InvalidAccountStatusError

class TestAccountInvariants(unittest.TestCase):
    """Test suite ensuring Account core data invariants remain protected."""

    def setUp(self) -> None:
        """Initializes a pristine Account instance before each test run."""
        self.sample_acc = Account(
            id="acc_iI1l3",
            acc_name="Test Acc",
            acc_type=AccType.CASH.value,
            amount=10000,  # Stored as an integer ($100.00 equivalent)
        )

    def test_account_initialization_safety(self):
        """Ensures core properties assign correctly and protect write-once invariants."""
        self.assertEqual(self.sample_acc.id, "acc_iI1l3")
        self.assertEqual(self.sample_acc.acc_name, "Test Acc")
        self.assertEqual(self.sample_acc.acc_type, AccType.CASH.value)
        self.assertEqual(self.sample_acc.acc_status, AccStat.ACTIVE.value)
        self.assertIsInstance(self.sample_acc.created_at, datetime)
        self.assertEqual(self.sample_acc.balance, 10000)

    def test_account_write_once_properties(self):
        """Ensures write-once invariants are protected."""
        with self.assertRaises(AttributeError):
            self.sample_acc.id = "acc_badOp" # type: ignore
        with self.assertRaises(AttributeError):
            self.sample_acc.acc_type = "crypto" # type: ignore
        with self.assertRaises(AttributeError):
            self.sample_acc.created_at = datetime.now() # type: ignore

    def test_account_property_setters_process_values_correctly(self):
        """Verifies account mutable properties preserve pipeline behavior"""
        with self.assertRaises(InvalidAmountError):
            self.sample_acc.balance = "invalid_amount"
        with self.assertRaises(InvalidAmountError):
            self.sample_acc.balance = -10
        with self.assertRaises(InvalidAccountStatusError):
            self.sample_acc.acc_status = "invalid_account_state"

    def test_invalid_initialization_raises_error(self):
        """Verifies that bad configuration arguments crash safely on instantiation."""

        # No empty string for id field
        with self.assertRaises(InvalidIDError):
            Account(
                id="",
                acc_name="Test",
                acc_type=AccType.BANK.value,
                amount=2000
            )
        # Names cannot be an empty string
        with self.assertRaises(AccNameError):
            Account(
                id="acc_e5Es5",
                acc_name="",
                acc_type=AccType.BANK.value,
                amount=2000
            )
        # Names must be at least 3 characters long
        with self.assertRaises(AccNameError):
            Account(
                id="acc_e5Es5",
                acc_name="Na",
                acc_type=AccType.BANK.value,
                amount=2000
            )
        # Account type cannot be empty
        with self.assertRaises(InvalidAccountTypeError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type="", # type: ignore
                amount=2000
            )
        # Account type must be a valid type
        with self.assertRaises(InvalidAccountTypeError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type="crypto", # type: ignore
                amount=2000
            )
        # Amount must be a positive integer
        with self.assertRaises(InvalidAmountError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type=AccType.MOBILE.value,
                amount="invalid_amount" # type: ignore
            )
        # Amount must be a positive integer
        with self.assertRaises(InvalidAmountError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type=AccType.MOBILE.value,
                amount=-1000
            )

    def test_credit_increases_balance_correctly(self):
        """Verifies credit transactions increment available balances cleanly."""
        self.sample_acc.credit(1000)
        self.assertEqual(self.sample_acc.balance, 11000)

    # Test that deactivated accounts cannot perform any transactions

    def test_debit_decreases_balance_correctly(self):
        """Verifies debit transactions decrement available balances cleanly."""
        self.sample_acc.debit(5000)
        self.assertEqual(self.sample_acc.balance, 5000)

    def test_negative_balance_invariant_enforcement(self):
        """Guarantees balances can never be forced beneath zero."""
        # Setting property balance beneath zero directly should raise a ExcessDebitError
        with self.assertRaises(InvalidAmountError):
            self.sample_acc.balance = -1

        # Debiting more than available assets should raise a InvalidAmountError
        with self.assertRaises(ExcessDebitError):
            self.sample_acc.debit(100000)

    def test_inactive_account_locks_transactions(self):
        """Verifies that locking/deactivating an account blocks credits and debits."""
        self.sample_acc.acc_status = AccStat.INACTIVE.value

        # Credits must be rejected on inactive files
        with self.assertRaises(AccStatusError):
            self.sample_acc.credit(5000)

        # Debits must be rejected on inactive files
        with self.assertRaises(AccStatusError):
            self.sample_acc.debit(2000)

    def test_conditional_deactivation_rules(self):
        """Ensures an account can only be deactivated if its balance is exactly zero."""
        # Balance is currently 10000 -> Should fail deactivation
        can_deactivate = self.sample_acc.deactivate_account()
        self.assertFalse(can_deactivate)
        self.assertEqual(self.sample_acc.acc_status, "active")

        # Empty the balance out
        self.sample_acc.debit(10000)
        
        # Balance is now 0 -> Should successfully deactivate
        can_deactivate_now = self.sample_acc.deactivate_account()
        self.assertTrue(can_deactivate_now)
        self.assertEqual(self.sample_acc.acc_status, "inactive")