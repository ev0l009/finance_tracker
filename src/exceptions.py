"""Custom Finance Tracker exceptions"""

class TrackerException(Exception):
    """Generic finace tracker exception."""
    pass

class InvalidOptionError(TrackerException):
    "Exception for invalid user inputs"
    pass

class NullEligibleAccountsError(TrackerException):
    """Exception for no accounts"""
    pass

