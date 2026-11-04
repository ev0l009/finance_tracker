- The App State/Context Pattern
- Dependency Injection
- Singleton-based Injection or a Global Registry.
- Pydantic models



1. Reframed Threat Model & Claims (Option A)

• Reference Exposure: The internal state uses mutable lists, but external layers only receive immutable tuple versions or generators of the transaction history to prevent accidental manipulation.
• Safety Bar: We drop any "un-breachable" claims. frozen=True is an anti-accident safety net for internal developer oversight, not a security sandbox against runtime hacking (object.__setattr__ easily bypasses it).
• Validation Scope: Loading validation catches malformed data and corruption, not logical tampering. If an amount is cleanly changed from 5,000 to 6,000, the loader accepts it.

2. State & Loading Failures (Option A)

• Balance Changes: No code path updates balances via dict keys. Dicts are purely short-lived serialization steps; the application core relies exclusively on the frozen Transaction properties.
• Handling Load Failures:
	• Must Do: Fail fast, raise a StorageCorruptionError, quarantine the bad JSON file immediately by duplicating it with a .corrupt extension, and halt execution.
	• Must Never Do: Never skip the record silently (calculates wrong balances) and never auto-wipe the file to a clean, empty baseline (destroys salvageable user history).

Below is the complete, consolidated invariant mapping. All canonical exception types are defined globally in exceptions.py and referenced directly here.

| Field / Rule | Illegal Condition | Canonical Exception Type | Enforcing Layer |
| :--- | :--- | :--- | :--- |
| IDs (id, source_acc_id, etc.) | Empty string, non-string types, or malformed prefix syntax (e.g., "acc_x") | InvalidIdentifierError | Entity |
| Account Name | Empty, string length < 4 or > 20 chars, or purely whitespace ("   ") | AccNameError | UI Input & Entity |
| Account Name | Duplicate name within the ledger database | AccNameError | Service |
| Account type | empty strings, invalid account type | `InvalidAccountTypeError` | UI Input & Entity |
| Account status | empty strings, invalid account status | `InvalidAccountStatusError` | UI Input & Entity |
| Transaction Amount | Zero, negative numbers, non-integers, boolean | InvalidAmountError | Entity |
| Transaction Amount | Amount greater than the source account's available balance | ExcessDebitError | Service |
| Account Balance | When transaction amount is more than available balance | ExcessDebitError | Service |
| Transfer Integrity | source_acc_id == target_acc_id identically during a transfer execution | SameAccountTransferError | Service & Entity |
| Timestamp / Date | Missing, malformed date input, or a calendar date in the future | InvalidTransactionDateError | UI Input & Entity |
| Transaction Type | Empty string, or value outside allowed types | InvalidTransactionTypeError | Entity |
| Category | Empty string, or custom string containing leading/trailing whitespace | InvalidCategoryError | UI Input & Entity |

4. Resolution of Open Cases


Case 1: Order of Operations (₦5,000 Expense)

1. Step 1: Build Transaction Record. Can raise entity errors (e.g., InvalidAmountError). Memory & Disk: Unchanged. (Reversible).
2. Step 2: Change Balance in Service. Can raise ExcessDebitError. Memory & Disk: Unchanged. (Reversible).
3. Step 3: Save to Disk. Can raise IOError. Memory holds the change, but Disk does not.
	• Mitigation: The Service layer catches the IOError, explicitly rolls back the in-memory balance change, and then allows the exception to bubble up. This keeps memory and disk in perfect sync.

Case 2: Malformed Stored Records

• Missing Keys: Missing JSON fields (causing a raw KeyError) represent bad physical storage and raise a StorageCorruptionError (inherits from a base infrastructure exception).
• Contextual Exceptions: The loading loop catches all inner entity validation errors and wraps them to append structural context:python
try:
    tx = Transaction(**record_dict)
except (InvalidAmountError, FutureDateError) as e:
    raise StorageCorruptionError(f"Corrupted row at Transaction ID {record_dict.get('id')}: {e}") from e
Use code with caution.

Case 4: Controlling "Now"

• Chosen Approach: Clock Dependency Injection. We pass a clock factory/interface to our code. Production code fetches standard local time, while test suites inject a frozen/mocked clock. This guarantees 100% deterministic test execution for the FutureDateError rule.

5. Architectural Log Summary


# ARCHITECTURAL DECISION LOG

## 1. Reference Isolation
Expose transactions to external layers strictly as read-only tuples to enforce an unalterable history against internal programmatic accidents.

## 2. Storage Hardening
Handle data structural failures on initialization with a custom `StorageCorruptionError`. Prevent automatic fallbacks to empty baselines; quarantine damaged ledger files immediately.

## 3. Clock Injection
Decouple time verification from hardware clocks across the entity and service boundaries to ensure deterministic test verification of future-date invariants.
Use code with caution.