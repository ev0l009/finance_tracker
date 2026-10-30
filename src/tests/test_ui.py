"""Unit tests for the User Interface presentation layer.

Simulates terminal user keypresses and captures print stream outputs to verify
menu routing choices, fallback defaults, and boundary constraints.
"""

import io
import unittest
from unittest.mock import patch
from models.types import MenuState
from ui import get_main_menu_state  # Adjust import based on where your UI module sits


class TestUserInterfaceRouting(unittest.TestCase):
    """Test suite for capturing terminal menu IO loops and state returns."""

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
        self.assertIn("Invalid selection. Try again...", console_output)