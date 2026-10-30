import unittest
from models.account import Account
from models.types import AccType, AccStat
from datetime import datetime

class TestAccountInvariants(unittest.TestCase):

    def setUp(self) -> None:
        self.sample_acc = Account(
            id="acc_iI1l3",
            acc_name="Test Acc",
            acc_type=AccType.CASH.value,
            amount=10000,
        )

    def test_account_initialization_safety(self):
        self.assertEqual(self.sample_acc.id, "acc_iI1l3")
        self.assertEqual(self.sample_acc.acc_name, "Test Acc")
        self.assertEqual(self.sample_acc.acc_type, AccType.CASH.value)
        self.assertEqual(self.sample_acc.acc_status, AccStat.ACTIVE.value)
        self.assertIsInstance(self.sample_acc.created_at, datetime)
        self.assertEqual(self.sample_acc.balance, 10000)

    def test_account_immutable_properties(self):
        with self.assertRaises(AttributeError):
            self.sample_acc.id = "acc_badOp" # type: ignore
        with self.assertRaises(AttributeError):
            self.sample_acc.acc_type = "crypto" # type: ignore
        with self.assertRaises(AttributeError):
            self.sample_acc.created_at = datetime.now() # type: ignore

    # Test account mutable properties still expected pipelines as applied with @property setter

    def test_invalid_initialization_raises_value_error(self):
        with self.assertRaises(ValueError):
            Account(
                id="",
                acc_name="Test",
                acc_type=AccType.BANK.value,
                amount=2000
            )
        with self.assertRaises(ValueError):
            Account(
                id="acc_e5Es5",
                acc_name="",
                acc_type=AccType.BANK.value,
                amount=2000
            )
        with self.assertRaises(ValueError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type="", # type: ignore
                amount=2000
            )
        with self.assertRaises(ValueError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type="crpto", # type: ignore
                amount=2000
            )
        with self.assertRaises(ValueError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type=AccType.MOBILE.value,
                amount="invalid_amount" # type: ignore
            )
        with self.assertRaises(ValueError):
            Account(
                id="acc_e5Es5",
                acc_name="test",
                acc_type="digital", 
                amount=-1000
            )

    def test_credit_increases_balance_correctly(self):
        self.sample_acc.credit(1000)
        self.assertEqual(self.sample_acc.balance, 11000)

    def test_debit_decreases_balance_correctly(self):
        self.sample_acc.debit(5000)
        self.assertEqual(self.sample_acc.balance, 5000)

    def test_negative_balance_invariant_enforcement(self):
        with self.assertRaises(ValueError):
            self.sample_acc.balance = -1

        with self.assertRaises(ValueError):
            self.sample_acc.debit(100000)