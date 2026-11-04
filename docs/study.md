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
| Account Name | Empty, string length < 4 or > 20 chars, or purely whitespace ("   ") | InvalidAccountNameError | UI Input & Entity |
| Account Name | Duplicate name within the ledger database (Case-Insensitive) | DuplicateAccountError | Service |
| Account Type / Status | Empty string, or value outside defined enums (e.g., Active/Suspended) | InvalidAccountStateError | UI Input & Entity |
| Transaction Amount | Zero, negative numbers, non-integers, booleans, or values > 2⁶³-1 | InvalidAmountError | Entity |
| Transaction Amount | Floating-point strings (e.g., "1,500.505") sent to currency parser | CurrencyParsingError | UI Input |
| Transaction Amount | Amount greater than the source account's available balance | ExcessDebitError | Service |
| Account Balance | Structural storage operation forcing a running balance < 0 | ExcessDebitError | Service |
| Transfer Integrity | source_acc_id == target_acc_id identically during a transfer execution | SameAccountTransferError | Service & Entity |
| Timestamp / Date | Missing, malformed date input, or a calendar date in the future | FutureDateError | UI Input & Entity |
| Transaction Type | Empty string, or value outside allowed directional types (Credit/Debit) | InvalidTransactionTypeError | Entity |
| Category | Empty string, or custom string containing leading/trailing whitespace | InvalidCategoryError | UI Input & Entity |


Deep-Dive Explanations & Boundary Mapping

• Account Name Constraints: A string consisting entirely of whitespace like "   " fails the len(name.strip()) >= 4 boundary check and throws InvalidAccountNameError. Duplicate tracking requires an aggregate evaluation of the collection, which is explicitly handled by the Service Layer querying the repository.
• Date Timezone Boundaries: "Today" is calculated using the user's local system timezone via a shared system clock utility. For a transaction entered at 12:30 AM, it is safely evaluated against that exact calendar date.
• Currency Conversion & Precision Protection: The UI layer converts fractional Naira strings to integer Kobo before invoking the Service or Entity layer. If a user inputs "1,500.50", the UI strips formatting and scales it to 150050. If a sub-kobo fractional value like "100.505" is entered, the UI parser immediately rejects it with a CurrencyParsingError instead of rounding or losing precision silently. Values exceeding a 64-bit integer limit are caught by the Entity boundary check.
• Date Utility Alignment: The entity's defensive check and the UI layer share the exact same system clock function interface, preventing drift or re-implementation bugs between input capture and entity creation.

4. Open Cases Resolved


Case 1: Order of Operations Lifecycle (₦5,000 Expense from Main Bank)

The application executes mutations in a strict transactional workflow to guarantee memory-to-disk consistency:
1. Step 1: Build the Transaction Record
	• Can it raise? Yes. If fields are malformed, it throws an entity validation error (e.g., InvalidAmountError, FutureDateError).
	• Failure State: Memory: Unchanged (original balances preserved). Disk: Unchanged. (Fully reversible; no cleanup needed).
2. Step 2: Change the Balance (Service Layer)
	• Can it raise? Yes. If the ₦5,000 deduction causes an overdraft, the Service layer throws ExcessDebitError.
	• Failure State: Memory: Unchanged (the operation checks balance invariants before executing mutations). Disk: Unchanged. (Fully reversible).
3. Step 3: Save to Disk
	• Can it raise? Yes. Disk full, file permission errors, or unexpected hardware faults can throw an IOError.
	• Failure State: Memory: Corrupted state alert! Memory now holds the modified account balance and the new transaction record, but the disk does not reflect this change.
	• Reversibility & Mitigation: To prevent this step from being an irreversible trap, the Service layer wraps Step 2 and Step 3 in an in-memory rollback block. If Step 3 raises an exception, the Service layer explicitly reverses the balance modification in memory before allowing the exception to bubble up. This ensures memory and disk stay synchronized.

Case 2: Malformed Stored Records & Extraction Strategy

• Missing Key Exceptions: A missing key like "category" causing a raw KeyError indicates structural storage degradation. This is represented by a dedicated StorageCorruptionError, which inherits directly from a base SystemInfrastructureError (distinct from user-facing business errors).
• Context-Aware Validation Failures: When an entity validation error (like InvalidAmountError) fires during a file load sequence, it must never escape un-translated. The loading loop catches all validation errors, reads the primary key context from the loop index or the record's raw id entry, and wraps it into a structured diagnostic wrapper:
python
try:
    tx = Transaction(**record_dict)
except (InvalidAmountError, FutureDateError, InvalidIdentifierError) as e:
    raise StorageCorruptionError(
        f"Corrupted record detected in storage during load at Transaction ID: {record_dict.get('id', 'UNKNOWN')}. Reason: {e}"
    ) from e
Use code with caution.

Case 4: Controlling "Now" for Time-Sensitive Invariants

• Decided Choice: Make today's date something the code under test doesn’t fetch itself (Clock Dependency Injection).
• Justification: Injecting an explicit clock provider or a date factory function into your services and entities completely decouples the business logic from the hardware clock. This guarantees that tests are 100% deterministic without relying on flaky real-world relative date calculations that shift depending on the day the test suite runs.
• Log Entry:DECISION LOG: Implemented an injectable system clock interface for all entity and service level date evaluations. Real-time executions default to datetime.date.today(), while test suites inject a frozen mock provider to ensure deterministic verification of the FutureDateError invariant.

5. Architectural Log Summary

markdown
# ARCHITECTURAL DECISION LOG

## 1. Threat Model Bounds
- **Decision:** Position `frozen=True` explicitly as defensive engineering against accidental programmatic mutations, not security sandboxing.
- **Enforcement:** Restrict raw list reference leaks; expose historical ledger entries only as read-only tuples.

## 2. Storage & Instantiation Security
- **Decision:** Disallow all direct dictionary-key modifications for balances. Utilize `StorageCorruptionError` to wrap and isolate structural JSON parsing faults and missing keys during initialization.
- **Safety Policy:** Quarantine corrupted files immediately on startup; completely block automated fallback to empty baselines without explicit user authorization.

## 3. Clock Isolation
- **Decision:** Implement explicit clock dependency injection across Entity and Service layers to ensure rock-solid, deterministic testing of the future-date invariant rule.
Use code with caution.
To finalize this iteration, should we design the structural layout of the StorageCorruptionError class in exceptions.py, or would you like to review the implementation details of the Clock Dependency Injection interface?
