"""Unit tests for the Transaction domain models.

Verifies immutability constraints, JSON schema hydration, serialization mappings,
and auto-generated timestamp behaviors.
"""

from datetime import datetime, timezone
import unittest
from models.transaction import DepositTrx, TransferTrx, WithdrawalTrx
from models.types import DepositTrxDict, TransferTrxDict, TrxType, WithdrawalTrxDict


class TestTransactionModels(unittest.TestCase):
    """Test suite ensuring Transaction dataclass invariants remain secure and protected."""

    def setUp(self) -> None:
        """Initializes raw test data structures mimicking JSON payloads."""
        self.raw_transfer_data: TransferTrxDict = {
            "id": "trx_Trf89",
            "amount": 25000,
            "source_acc_id": "acc_snd11",
            "target_acc_id": "acc_rcv22",
            "transaction_type": "transfer",
            "timestamp": "2026-10-31T00:00:00",
        }
        self.raw_withdrawal_data: WithdrawalTrxDict = {
            "id": "trx_Uz9yZ",
            "amount": 500,
            "timestamp": "2026-10-28T22:20:17+00:00",
            "category": "food",
            "transaction_type": "withdraw"
        }
        self.raw_deposit_data: DepositTrxDict = {
            "id": "trx_7Ogg5",
            "amount": 5000,
            "acc_id": "acc_Hmpxy",
            "timestamp": "2026-10-29T22:31:32+00:00",
            "transaction_type": "deposit"
        }

    def test_transaction_immutability(self) -> None:
        """Guarantees frozen=True blocks runtime mutation attempts on ledger entries."""
        trf_tx = TransferTrx.from_json(self.raw_transfer_data)
        wdl_tx = WithdrawalTrx.from_json(self.raw_withdrawal_data)
        dep_tx = DepositTrx.from_json(self.raw_deposit_data)

        # Isolated property checks ensure one failure doesn't bypass subsequent checks
        with self.assertRaises(AttributeError):
            trf_tx.amount = 50000  # type: ignore
        with self.assertRaises(AttributeError):
            wdl_tx.amount = 50000  # type: ignore
        with self.assertRaises(AttributeError):
            dep_tx.amount = 50000  # type: ignore

        with self.assertRaises(AttributeError):
            trf_tx.id = "new_id"  # type: ignore
        with self.assertRaises(AttributeError):
            wdl_tx.id = "new_id"  # type: ignore
        with self.assertRaises(AttributeError):
            dep_tx.id = "new_id"  # type: ignore

    def test_transfer_hydration_and_serialization_cycle(self) -> None:
        """Verifies full round-trip conversion from dictionary to object back to dictionary."""
        # 1. Hydrate from raw dictionary data
        tx = TransferTrx.from_json(self.raw_transfer_data)

        self.assertEqual(tx.id, "trx_Trf89")
        self.assertEqual(tx.amount, 25000)
        self.assertEqual(tx.source_acc_id, "acc_snd11")
        self.assertEqual(tx.target_acc_id, "acc_rcv22")
        self.assertEqual(tx.transaction_type, TrxType.TRANSFER.value)
        self.assertEqual(tx.timestamp, "2026-10-31T00:00:00")

        # 2. Serialize back into standard data dictionary layout
        serialized_map = tx.to_dict()

        self.assertEqual(serialized_map["id"], "trx_Trf89")
        self.assertEqual(serialized_map["amount"], 25000)
        self.assertEqual(serialized_map["source_acc_id"], "acc_snd11")
        self.assertEqual(serialized_map["target_acc_id"], "acc_rcv22")
        self.assertEqual(serialized_map["transaction_type"], "transfer")

    def test_withdrawal_hydration_and_serialization_cycle(self) -> None:
        """Verifies round-trip hydration and dictionary mappings for withdrawals."""
        tx = WithdrawalTrx.from_json(self.raw_withdrawal_data)

        self.assertEqual(tx.id, "trx_Uz9yZ")
        self.assertEqual(tx.amount, 500)
        self.assertEqual(tx.category, "food")
        self.assertEqual(tx.transaction_type, TrxType.WITHDRAW.value)

        serialized_map = tx.to_dict()
        self.assertEqual(serialized_map["category"], "food")
        self.assertEqual(serialized_map["transaction_type"], "withdraw")

    def test_deposit_hydration_and_serialization_cycle(self) -> None:
        """Verifies round-trip hydration and dictionary mappings for deposits."""
        tx = DepositTrx.from_json(self.raw_deposit_data)

        self.assertEqual(tx.id, "trx_7Ogg5")
        self.assertEqual(tx.amount, 5000)
        self.assertEqual(tx.acc_id, "acc_Hmpxy")
        self.assertEqual(tx.transaction_type, TrxType.DEPOSIT.value)

        serialized_map = tx.to_dict()
        self.assertEqual(serialized_map["acc_id"], "acc_Hmpxy")
        self.assertEqual(serialized_map["transaction_type"], "deposit")

    def test_missing_timestamp_falls_back_to_generated_default(self) -> None:
        """Verifies that payloads omitting timestamps automatically fall back to current UTC."""
        payload_without_time = {    # type: ignore
            "id": "trx_Dep01",
            "amount": 10000,
            "acc_id": "acc_chk55",
        }

        tx = DepositTrx.from_json(payload_without_time)  # type: ignore

        self.assertIsNotNone(tx.timestamp)
        if isinstance(tx.timestamp, datetime):
            self.assertEqual(tx.timestamp.tzinfo, timezone.utc)


if __name__ == "__main__":
    unittest.main()
