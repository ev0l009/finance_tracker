def validate_acc_name(value: str, value_map: dict[str, str]):
    if not value.strip():
        raise ValueError("\nAccount name cannot be empty")

    if len(value) < 3:
        raise ValueError("Account name cannot be less than 3 characters\n")
    
    if value in value_map.values():
        raise ValueError("\nAn account with this name already exists.\n")

    return value.strip()

def validate_amount(amount: str):
    if not amount.strip():
        return 0

    try:
        start_amt = int(amount)
    except ValueError:
        raise ValueError("\nStarting amount must be an integer.\n")

    if start_amt < 0:
        raise ValueError("\nStarting amount cannot be a negative value.")

    return start_amt