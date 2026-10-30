"""Unit tests for input validation utilities.

Verifies that name trimming, deduplication constraints, integer parsing,
and negative currency guards function flawlessly under structural test suites.
"""

import unittest
from exceptions import AccNameError, InvalidAmountError
from utils import validate_acc_name, validate_amount


class TestUtilsValidation(unittest.TestCase):
    """Test suite verifying input sanitization and domain rule execution."""

    def setUp(self) -> None:
        """Initializes a simulated registry of existing names for collision testing."""
        self.existing_names = {
            "acc_11111": "checking account",
            "acc_22222": "savings wallet",
            "acc_33333": "emergency reserve",
        }

    # --- ACCOUNT NAME VALIDATION TESTS ---

    def test_validate_acc_name_happy_path(self) -> None:
        """Ensures valid unique names are accepted and returned safely stripped."""
        result = validate_acc_name("  Business Fund  ", self.existing_names)
        self.assertEqual(result, "Business Fund")

    def test_validate_acc_name_empty_or_whitespace_raises_error(self) -> None:
        """Verifies that completely blank or space-only names are blocked."""
        with self.assertRaises(AccNameError) as context:
            validate_acc_name("    ", self.existing_names)
        self.assertIn("cannot be empty", str(context.exception))

    def test_validate_acc_name_too_short_raises_error(self) -> None:
        """Verifies that stripped names under 3 characters are rejected."""
        with self.assertRaises(AccNameError) as context:
            validate_acc_name("  ab  ", self.existing_names)
        self.assertIn("cannot be less than 3 characters", str(context.exception))

    def test_validate_acc_name_duplicate_raises_error(self) -> None:
        """Guarantees that duplicate account names cause a soft validation failure."""
        with self.assertRaises(AccNameError) as context:
            validate_acc_name("checking account", self.existing_names)
        self.assertIn("already exists", str(context.exception))

    # --- AMOUNT VALIDATION TESTS ---

    def test_validate_amount_happy_path(self) -> None:
        """Ensures numeric strings are correctly parsed into whole integers."""
        self.assertEqual(validate_amount("  5000  "), 5000)
        self.assertEqual(validate_amount("0"), 0)

    def test_validate_amount_empty_returns_zero(self) -> None:
        """Verifies that pressing Enter (blank string) safe-defaults to a zero balance."""
        self.assertEqual(validate_amount("   "), 0)

    def test_validate_amount_non_integer_raises_error(self) -> None:
        """Verifies that strings containing decimals or non-numeric digits are blocked."""
        # Decimal numbers are rejected (system processes balances as whole integers)
        with self.assertRaises(InvalidAmountError) as context:
            validate_amount("150.50")
        self.assertIn("must be a valid whole number integer", str(context.exception))

        # Alpha characters are rejected
        with self.assertRaises(InvalidAmountError):
            validate_amount("five_hundred")

    def test_validate_amount_negative_raises_error(self) -> None:
        """Guarantees that negative numbers are blocked during parsing operations."""
        with self.assertRaises(InvalidAmountError) as context:
            validate_amount("-250")
        self.assertIn("cannot be a negative value", str(context.exception))


if __name__ == "__main__":
    unittest.main()
