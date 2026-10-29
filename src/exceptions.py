"""Custom exceptions for the Finance Tracker application.

Provides a unified hierarchical exception structure. All custom domain 
errors inherit from the base TrackerException to allow generic catching 
at the application's root loop.
"""


class TrackerException(Exception):
    """Base exception for all errors raised by the Finance Tracker application."""

    pass


class InvalidOptionError(TrackerException):
    """Raised when a user provides an unrecognized or invalid menu input selection."""

    pass


class NullEligibleAccountsError(TrackerException):
    """Raised when an operation requires accounts to exist but none are found."""

    pass


class AccNameError(TrackerException):
    """Raised when an account name is structurally invalid, reserved, or a duplicate."""

    pass


class InvalidAmountError(TrackerException):
    """Raised when a monetary value is zero, negative, or formatted incorrectly."""

    pass