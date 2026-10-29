"""Input validation utilities for the Finance Tracker application.

Provides system-wide input scrubbing and validation routines that enforce
business rules, raising domain-specific exceptions on failure.
"""

from exceptions import AccNameError, InvalidAmountError


def validate_acc_name(value: str, existing_names: dict[str, str]) -> str:
    """Validates an account name against length constraints and duplicates.

    Args:
        value: The raw string input provided by the user.
        existing_names: A mapping containing current system account names.

    Returns:
        str: The safely stripped, validated account name string.

    Raises:
        AccNameError: If the name is blank, under 3 characters, or a duplicate.
    """
    cleaned_name = value.strip()

    if not cleaned_name:
        raise AccNameError("Account name cannot be empty.")

    if len(cleaned_name) < 3:
        raise AccNameError("Account name cannot be less than 3 characters.")

    if cleaned_name in existing_names.values():
        raise AccNameError("An account with this name already exists.")

    return cleaned_name


def validate_amount(amount: str) -> int:
    """Scrubs and parses a raw user string into a valid integer amount.

    Args:
        amount: The raw numeric string input provided by the user.

    Returns:
        int: The parsed whole currency integer value. Returns 0 if empty.

    Raises:
        InvalidAmountError: If the input cannot be parsed or is negative.
    """
    cleaned_amount = amount.strip()
    
    if not cleaned_amount:
        return 0

    try:
        parsed_amt = int(cleaned_amount)
    except ValueError:
        raise InvalidAmountError("Amount must be a valid whole number integer.")

    if parsed_amt < 0:
        raise InvalidAmountError("Amount cannot be a negative value.")

    return parsed_amt
