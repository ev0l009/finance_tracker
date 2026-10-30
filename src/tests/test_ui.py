"""Unit tests for the User Interface presentation layer.

Simulates terminal user keypresses and captures print stream outputs to verify
menu routing choices, fallback defaults, and boundary constraints.
"""

import io
import unittest
from unittest.mock import patch
from models.types import MenuState, AccDashState, AccType
from ui import get_main_menu_state, get_acc_dash_state, get_account_type, select_acc, get_category
from exceptions import InvalidOptionError, NullEligibleAccountsError

class TestUserInterfaceRouting(unittest.TestCase):
    """Test suite for capturing terminal menu IO loops and state returns."""
    def setUp(self):
        self.acc_map = {
            "acc_abc01": "Test Bank Acc",
            "acc_234de": "Test Cash Acc",
            "acc_fgh56": "Test Savings Acc",
            "acc_789ij": "Test Mobile Acc"
        }
        self.empty_acc_map = {}

    @patch("builtins.input", return_value="1")
    def test_get_main_menu_state_valid_choice(self, mock_input) -> None:
        """Ensures choosing a valid menu option routes to the correct target state."""
        # Act: Execute UI logic with simulated input '1'
        selected_state = get_main_menu_state()

        # Assert: Verify it maps straight to the expected Enum value string
        self.assertEqual(selected_state, MenuState.CREATE_ACCOUNT.value)

    @patch("builtins.input", return_value="8")
    def test_get_main_menu_state_exit_choice(self, mock_input) -> None:
        """Ensures option 8 cleanly routes straight to the system exit state."""
        selected_state = get_main_menu_state()
        self.assertEqual(selected_state, MenuState.EXIT.value)

    @patch("builtins.input", return_value="invalid_selection_9")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_get_main_menu_state_invalid_choice_handling(self, mock_stdout, mock_input) -> None:
        """Verifies that an out-of-bounds user string falls back to the main dashboard state."""
        # Act: Pass bad key input, intercepting console prints
        selected_state = get_main_menu_state()

        # Assert 1: It should safely loop back by returning the default dashboard state string
        self.assertEqual(selected_state, MenuState.DASHBOARD.value)

        # Assert 2: Verify the UI printed out the invalid warning banner to the user
        console_output = mock_stdout.getvalue()
        self.assertIn("\n  [!] Invalid choice. Please try again.", console_output)


    @patch("builtins.input", return_value="3")
    def test_get_acc_dash_state_valid_choice(self, mock_input):
        selected_state = get_acc_dash_state("Test Acc")
        self.assertEqual(selected_state, AccDashState.WITHRAWAL.value)

    @patch("builtins.input", return_value="5")
    def test_get_acc_dash_state_exit_choice(self, mock_input):
        selected_state = get_acc_dash_state("Test Acc")
        self.assertEqual(selected_state, AccDashState.RETURN.value)

    @patch("builtins.input", return_value="invalid_selection")
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_get_acc_dash_state_invalid_choice(self, mock_stdout, mock_input):
        selected_state = get_acc_dash_state("Test Acc")
        self.assertIn(selected_state, AccDashState.ACC_DASH.value)

        console_output = mock_stdout.getvalue()
        self.assertIn("\n  [!] Invalid choice. Please try again.", console_output)


    @patch("builtins.input", return_value="3")
    def test_get_account_type_valid_choice(self, mock_input):
        selected_acc_type = get_account_type()
        self.assertEqual(selected_acc_type, AccType.SAVINGS.value)

    @patch("builtins.input", return_value="invalid_selection_5")
    def test_get_account_type_invalid_choice_raises_invalid_option_error(self, mock_input):
        with self.assertRaises(InvalidOptionError):
            get_account_type()


    @patch("builtins.input", return_value="2")
    def test_select_acc_valid_choice(self, mock_input):
        selected_acc_id = select_acc(self.acc_map)
        self.assertEqual(selected_acc_id, "acc_234de")

    @patch("builtins.input", return_value="invalid_selection_5")
    def test_select_acc_invalid_choice_raises_invalid_option_error(self, mock_input):
        with self.assertRaises(InvalidOptionError):
            select_acc(self.acc_map)

    def test_select_acc_empty_acc_map_raises_null_eligible_accounts_error(self):
        with self.assertRaises(NullEligibleAccountsError):
            select_acc(self.empty_acc_map)


    @patch("builtins.input", return_value="5")
    def test_get_category_valid_choice(self, mock_input):
        selected_cat = get_category()
        self.assertEqual(selected_cat, "health")

    @patch("builtins.input", return_value="invalid_selection_6")
    def test_get_category_invalid_selection_raises_invalid_option_error(self, mock_input):
        with self.assertRaises(InvalidOptionError):
            get_category()