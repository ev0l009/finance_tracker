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

class AccNameError(TrackerException):
    """Exceptions related to invalid and duplicate account names"""
    pass

class InvalidAmountError(TrackerException):
    """Amount related errors"""
    pass