"""Handles validation of user inputs"""

from exceptions import AccNameError, InvalidAmountError

def validate_acc_name(value: str, value_map: dict[str, str]):
    """Validates account name and returns a stripped string"""

    if not value.strip():
        raise AccNameError("\nAccount name cannot be empty")

    if len(value) < 3:
        raise AccNameError("Account name cannot be less than 3 characters\n")
    
    if value in value_map.values():
        raise AccNameError("\nAn account with this name already exists.\n")

    return value.strip()

def validate_amount(amount: str):
    """Validates user input and returns a integer"""
    if not amount.strip():
        return 0

    try:
        start_amt = int(amount)
    except ValueError:
        raise InvalidAmountError("\nStarting amount must be an integer.\n")

    if start_amt < 0:
        raise InvalidAmountError("\nStarting amount cannot be a negative value.")

    return start_amt