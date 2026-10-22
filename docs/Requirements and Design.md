# Personal Finance & Wallet Manager

## 1. Requirements

### 1.1 Multi-Account Ledger

The system must centralize management for various financial accounts, such as:

* Cash
* Bank accounts
* Wallets

Each account is treated as an independent sub-ledger.

The system must support:

* Account creation
* Listing available accounts
* Accessing a specific account
* Account deactivation
* Account archival/retrieval

---

### 1.2 Atomic Mutations

Income, expenses, and transfers must immediately produce accurate mathematical changes to the affected accounts.

All financial mutations must maintain a transparent audit trail.

Internal transfers between accounts owned by the same user must **not affect aggregate net balance**, because money is being moved rather than earned or spent.

---

### 1.3 Dynamic Ledger Queries

Historical transaction logs serve as the application's **single source of truth**.

The ledger must support:

* Transaction tracking
* Search
* Filtering
* Transaction detail views
* Account activity
* Concise financial overviews
* Historical financial reporting

All queries and reports must remain mathematically consistent with the underlying ledger.

---

### 1.4 Persistent Data Storage

Application data must persist between sessions.

Users should be able to exit the application and return later without losing their accounts, balances, or transaction history.

---

### 1.5 Intuitive CLI Interface

The terminal interface should be:

* Simple
* Predictable
* Easy to navigate
* Clear when displaying errors
* Clear when displaying financial information

The UI should not contain financial logic itself.

---

### 1.6 Error Handling & Testing

The application must:

* Handle relevant errors without terminating unexpectedly
* Provide meaningful error messages
* Protect financial state from invalid operations
* Have automated test coverage for:

  * Success paths
  * Error paths
  * Edge cases
  * Persistence behavior
  * Transaction consistency

---

### 1.7 Documentation

Documentation should provide enough information for both users and developers to quickly understand:

* What the application does
* How the system is structured
* How accounts and transactions work
* How the data is stored
* How to run the application
* How to run the tests

---

# 2. Assumptions

## 2.1 Permanent Data Retention

Accounts cannot be permanently hard-deleted from the database.

Instead, accounts transition between states such as:

```text
Active → Inactive
```

This preserves historical financial context and prevents historical transactions from losing their account references.

---

## 2.2 Local Single-User Context

The application runs entirely within a local terminal environment.

The current version assumes:

* One local user
* No authentication system
* No network synchronization
* No cloud storage
* Local operating-system file permissions provide the primary data-access boundary

---

## 2.3 Currency Representation

Financial values use the **Minor Units / Integer Pattern**.

Examples:

```text
$100.00 → 10000
$50.25  → 5025
```

All financial values are therefore represented as Python `int` values rather than `float` values.

This avoids floating-point rounding problems.

---

# 3. Resolved Ambiguities

## 3.1 What Does "Empty Account" Mean?

An account is considered empty when:

```text
balance == 0
```

An account containing any positive balance is not considered empty.

### Resolution

An account may only be deactivated when its balance is exactly zero.

If funds remain, the user must transfer them elsewhere before deactivation.

---

# 4. Financial Overview & Audit Reporting

## 4.1 Core Objective

Provide users with a concise, time-bound overview of their financial state.

Reports should be able to show:

* Total income
* Total expenses
* Spending categories
* Account activity
* Relevant transaction history

---

## 4.2 Income & Expense Logic

### Included

Only deposits and withdrawals directly affect aggregate income/expense calculations.

* Deposits → Total Income
* Withdrawals → Total Expenses

### Excluded

Internal transfers are excluded from income and expense calculations.

This prevents the same money from being counted as both income and expense when moved between the user's own accounts.

---

## 4.3 Transfer Rules

Transfers must remain fully visible in the transaction history even though they do not affect aggregate net income.

Each side of a transfer is associated with the relevant source/destination account.

Transfers should be clearly identifiable as:

```text
transaction_type = "transfer"
```

### Audit Trail

Transfers must appear under:

```text
Account Activity
```

This preserves an accurate historical record of where money moved.

---

## 4.4 Report Filters

Reports should support flexible filtering.

### Timeframes

Examples:

* This Week
* Last 7 Days
* Last Month
* Custom date range

### Transaction Types

* Deposits
* Expenses / Withdrawals
* Transfers

### Categories

Reports may be filtered by specific expense categories.

---

# 5. Business Rules

## 5.1 Account Management Rules

### Name Uniqueness

Every account name must be unique.

Comparison should be case-insensitive.

For example:

```text
Main Bank
main bank
MAIN BANK
```

must be treated as the same account name.

---

### Account Name Length

Account names must:

* Contain at least 4 characters
* Contain no more than 20 characters
* Not consist entirely of whitespace

---

### Account Initialization

A newly created account defaults to:

```python
balance = 0
```

unless a custom positive opening balance is explicitly supplied.

---

### Zero-Balance Deactivation

An account can only be deactivated when:

```python
balance == 0
```

If funds exist, they must first be transferred out.

---

### Inactive Account Visibility

Inactive accounts should be hidden from normal transaction-selection menus.

They remain accessible through an archival/account-management interface.

---

## 5.2 Transaction & Balance Rules

### Overdraft Protection

A withdrawal must be rejected when:

```python
amount > account.balance
```

Negative account balances are prohibited.

---

### Self-Transfer Prevention

A transfer must be rejected when:

```python
source_account_id == destination_account_id
```

An account cannot transfer money to itself.

---

### Transaction Immutability

Once a transaction has been committed to the ledger, it cannot be edited or modified.

To correct an erroneous transaction, a counter-balancing transaction must be created.

---

# 6. Transaction Integrity & Atomicity

## 6.1 Core Objective

Financial operations must preserve data consistency.

A transfer must be **atomic**:

> Either the entire transfer succeeds, or no part of it becomes committed state.

A "half transfer" must never exist in the application.

---

## 6.2 Transfer Execution Workflow

### Step 1 — Validation

Validate:

* Source account
* Destination account
* Account activity state
* Transfer amount
* Available balance
* Self-transfer condition

---

### Step 2 — Staging

Calculate the effects of both sides of the transfer in memory before committing the primary state changes.

Example:

```text
Source:
    balance -= amount

Destination:
    balance += amount
```

These changes remain staged until validation and processing have completed successfully.

---

### Step 3 — Commit

If the entire operation succeeds:

```text
Commit all staged changes
```

---

### Step 4 — Failure / Rollback

If an error occurs before commitment:

```text
Discard staged changes
```

No partial transaction should reach persistent storage.

---

## 6.3 Financial Audit Impact

### Zero Partial State

The system must never contain a committed transfer where only one side exists.

### Audit Integrity

Only fully committed transfers should appear in:

* Account activity
* Transaction history
* Reporting logs

---

# 7. Transaction Model Integrity

The transaction schema should prevent invalid states from being created.

Transactions should be immutable after construction.

## 7.1 Frozen Dataclass

The intended model is:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction:
    pass
```

`frozen=True` prevents direct mutation after construction.

---

## 7.2 Validation Before Construction

Transaction validation should ensure that invalid transaction objects cannot be created in the first place.

A validation hook may be implemented using:

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Transaction):

    def __post_init__(self):
        pass
```

### Frozen Dataclass Consideration

Because frozen dataclasses prevent normal attribute assignment, fields that must be normalized or transformed inside `__post_init__` require:

```python
object.__setattr__(self, "field_name", value)
```

rather than:

```python
self.field_name = value
```

---

# 8. Account State Invariants

Business rules should be enforced as close as possible to the state they protect.

## 8.1 Balance Setter

`balance` changes over time, but every write must satisfy the application's balance rules.

A property with a setter can be used to intercept balance mutations:

```python
@property
def balance(self):
    ...
    
@balance.setter
def balance(self, value):
    ...
```

This makes the balance constraint part of the object's runtime invariant rather than merely an external guideline.

---

## 8.2 Account Field Mutability

The intended mutability model is:

| Field          | Mutability                       |
| -------------- | -------------------------------- |
| `account_type` | Write-once                       |
| `id`           | Write-once                       |
| `created_at`   | Write-once                       |
| `balance`      | Mutable through validated setter |
| `name`         | Mutable through validated setter |

This means:

* `id` should not change after creation.
* `account_type` should not change after creation.
* `created_at` should not change after creation.
* `balance` may change, but only through validation.
* `name` may be changed because users are allowed to rename accounts.

---

# 9. Constrained Values & Enums

Where a field can only contain a defined set of states, an `Enum` should be used rather than arbitrary strings.

For example:

```python
from enum import Enum


class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
```

---

## 9.1 Enum Access

```python
item = Status.PENDING

print(item)
print(item.name)
print(item.value)
```

Conceptually:

```text
Status.PENDING
PENDING
pending
```

---

## 9.2 Enum Lookup

Lookup by value:

```python
Status("completed")
```

Lookup by name:

```python
Status["FAILED"]
```

---

## 9.3 Enum Iteration

```python
for status in Status:
    print(f"{status.name} -> {status.value}")
```

Enums should be considered for constrained fields such as:

* Account status
* Account type
* Transaction type

This prevents arbitrary string values from entering the system.

---

# 10. Architecture

The application follows a **Three-Tier Local Architecture** optimized for an interactive CLI environment.

The main principle is to separate:

```text
User Interaction
        ↓
Business Logic
        ↓
Persistence
```

This prevents changes to the CLI/menu system from accidentally affecting financial calculations.

---

## 10.1 Architecture Overview

```text
┌───────────────────────────────┐
│     Interactive Text Menus    │
│                               │
│   Continuous while loop       │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Command Parser          │
│                               │
│ Validates menu inputs,        │
│ numbers, dates, etc.          │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│        Service Layer          │
│                               │
│ Ledger math, transfers,       │
│ business rules                │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Persistence Layer       │
│                               │
│ Atomic JSON reads/writes      │
└───────────────────────────────┘
```

---

# 11. Architectural Responsibilities

## 11.1 Interface Tier

Responsible for:

* Terminal interaction
* `print()`
* `input()`
* Menu rendering
* Basic input validation
* Displaying formatted tables
* Displaying summaries
* Presenting errors to the user

The interface layer should not contain financial business logic.

---

## 11.2 Logic / Service Tier

The service layer is the core engine of the application.

Responsible for:

* Deposits
* Withdrawals
* Transfers
* Balance mutations
* Business rule enforcement
* Account operations
* Transaction creation
* Raising domain-specific exceptions

---

## 11.3 Storage / Persistence Tier

Responsible for:

* File I/O
* JSON serialization
* JSON deserialization
* Loading application state
* Saving application state
* Timestamp conversion
* Atomic file replacement

The persistence layer translates between:

```text
JSON ↔ Python objects
```

---

# 12. Proposed Project Structure

```text
finance_ledger/
│
├── data/
│   └── ledger.json
│
├── src/
│   ├── main.py
│   │
│   ├── ui/
│   │   ├── menus.py
│   │   └── validators.py
│   │
│   ├── services/
│   │   ├── ledger_service.py
│   │   ├── models.py
│   │   └── exceptions.py
│   │
│   └── storage/
│       └── file_manager.py
│
└── tests/
    └── test_ledger.py
```

### Responsibilities

| File                         | Responsibility                                    |
| ---------------------------- | ------------------------------------------------- |
| `main.py`                    | Application entry point and main menu loop        |
| `ui/menus.py`                | Menus and transaction-log presentation            |
| `ui/validators.py`           | Console input validation                          |
| `services/ledger_service.py` | Deposits, withdrawals, transfers, business rules  |
| `services/models.py`         | `Account`, `Transaction`, and related dataclasses |
| `services/exceptions.py`     | Domain-specific exceptions                        |
| `storage/file_manager.py`    | JSON loading, saving, and atomic writes           |
| `data/ledger.json`           | Local persistent data                             |
| `tests/test_ledger.py`       | Automated test suite                              |

---

# 13. Data Model

The application maintains its persistent state inside a single local JSON document.

Python `dataclass` objects represent the corresponding domain entities in memory.

---

## 13.1 Account Entity

An account contains:

* `id`
* `name`
* `account_type`
* `balance`
* `is_active`
* `created_at`

Example:

```json
{
    "id": "acc_01J8Y",
    "name": "Main Bank",
    "account_type": "bank",
    "balance": 125050,
    "is_active": true,
    "created_at": "2026-09-23T10:00:00Z"
}
```

---

## 13.2 Transaction Entity

The transaction entity provides a unified representation for:

* Deposits
* Withdrawals
* Transfers

Standard single-account transactions may not require both account references.

Transfers require references to both:

* Source account
* Destination account

Financial values are stored as integers representing minor currency units.

---

# 14. Proposed JSON Storage Structure

```json
{
    "accounts": {
        "acc_01J8Y": {
            "id": "acc_01J8Y",
            "name": "Main Bank",
            "account_type": "bank",
            "balance": 125050,
            "account_status": "active",
            "created_at": "2026-09-23T10:00:00Z"
        }
    },
    "transactions": [
        {
            "id": "tx_99A1Z",
            "transaction_type": "transfer",
            "amount": 15000,
            "source_account_id": "acc_01J8Y",
            "destination_account_id": "acc_02K9X",
            "category": "savings_allocation",
            "description": "Monthly savings transfer",
            "timestamp": "2026-09-23T11:30:00Z"
        }
    ]
}
```

---

## 14.1 Data Model Review Flags

Before implementation, the transaction schema should be finalized.

The original design contained an example where:

```text
transaction id = tx_99A1Z
destination_account_id = tx_99A1Z
```

This appears to reference the transaction itself rather than an account.

Additionally, the original sample contained two transactions with the same transaction ID.

These should be resolved before implementation.

### Required invariants

At minimum:

```text
Transaction IDs must be unique.
Account IDs must be unique.
source_account_id must reference an account.
destination_account_id must reference an account.
```

For deposits/withdrawals, the account-reference semantics should also be explicitly defined rather than reusing transfer fields ambiguously.

---

# 15. Persistence Strategy

The application uses:

```text
data/ledger.json
```

as its local persistence layer.

JSON provides a simple and transparent storage mechanism appropriate for a standalone CLI application.

---

# 16. Atomic File Persistence

## 16.1 The Risk

Directly overwriting `ledger.json` creates a corruption risk.

If the program or computer terminates while the file is being written, the resulting JSON may be incomplete or unreadable.

---

## 16.2 Atomic Replacement Strategy

The application writes to a temporary file first:

```text
data/ledger.json.tmp
```

Workflow:

```text
Python state
     ↓
Serialize
     ↓
ledger.json.tmp
     ↓
Successful write
     ↓
os.replace()
     ↓
ledger.json
```

Python's:

```python
os.replace()
```

is used to replace the existing production file with the successfully written temporary file.

This prevents the application from intentionally leaving behind a partially written production ledger.

---

# 17. Timestamp Serialization

JSON cannot directly serialize objects such as:

```python
datetime.datetime
```

Therefore the persistence layer performs conversion in both directions.

## 17.1 Loading

Timestamp strings such as:

```text
2026-09-23T10:00:00Z
```

are converted into Python datetime objects using:

```python
datetime.fromisoformat()
```

---

## 17.2 Saving

Python datetime objects are converted back into serializable timestamp strings before being written to JSON.

---

# 18. Error-Handling Strategy

The application follows a **Catch & Recover** model.

Errors are handled at the layer where they are most meaningful, preventing unnecessary crashes and exposing implementation tracebacks to normal users.

---

## 18.1 UI / Validation Errors

### Trigger

Occurs while processing interactive keyboard input.

Examples:

* Non-numeric amount
* Invalid menu choice
* Invalid date format

### Handling

The UI catches native exceptions such as:

```python
ValueError
```

and re-renders the input prompt.

Example:

```text
⚠️ Validation Error:
Please enter a valid numeric amount.
```

---

# 19. Domain / Business Rule Errors

### Trigger

Occurs inside the service layer after input has passed basic type validation but violates a financial rule.

Examples:

* Insufficient funds
* Inactive account
* Duplicate account name
* Self-transfer
* Invalid amount

### Handling

The service layer raises semantic domain exceptions.

Examples:

```python
InsufficientFundsError
AccountInactiveError
```

The application boundary catches these exceptions and displays a clean transaction-denial message.

---

# 20. Storage Errors

### Trigger

Occurs while loading or saving persistent data.

Examples:

* Corrupted JSON
* Invalid JSON syntax
* File read/write failure

### Current Proposed Handling

The storage engine catches:

```python
json.JSONDecodeError
```

and initializes:

```python
{
    "accounts": {},
    "transactions": []
}
```

as a safety baseline while displaying a diagnostic warning.

### Review Flag

The exact recovery policy for corrupted financial data should be finalized before implementation.

Automatically replacing corrupted financial data with an empty ledger can potentially hide or overwrite access to existing financial history.

A safer implementation may eventually require:

```text
Detect corruption
     ↓
Preserve corrupted file
     ↓
Create backup/quarantine copy
     ↓
Notify user
     ↓
Attempt recovery / require explicit action
```

This should be treated as a design decision rather than assumed behavior.

---

# 21. Domain Exception Catalogue

| Exception                           | Purpose                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------ |
| `InsufficientFundsError`            | Account balance is lower than the requested transaction amount                       |
| `NegativeAmountError`               | Negative amount supplied                                                             |
| `InvalidFieldAttributeError`        | Field contains invalid or insufficient data                                          |
| `DuplicateAccountNameError`         | Account name already exists                                                          |
| `InterAccountTransferMismatchError` | Transfer debits the source but fails to credit the destination                       |
| `DormantAccountError`               | Transaction targets an archive-only/closed account                                   |
| `FutureDatedTransactionError`       | Transaction timestamp is in the future when real-time historical logging is required |
| `AccountInactiveError`              | Account exists but is disabled, archived, or frozen                                  |
| `AccountNotFoundError`              | Referenced account cannot be found                                                   |

---

# 22. Testing Strategy

Testing uses `pytest` and is divided into three levels:

```text
┌──────────────────────────┐
│     1. Unit Tests        │
│                          │
│ Core calculations +      │
│ domain rules             │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   2. Integration Tests   │
│                          │
│ Serialization +          │
│ persistence              │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│    3. UI / Smoke Tests   │
│                          │
│ Interactive CLI flows    │
└──────────────────────────┘
```

---

# 23. Unit Testing

## Scope

Unit tests focus on isolated business logic and validation.

They should not depend on:

* Real files
* The terminal
* User input

---

## Examples

### Deposit

Given:

```text
Initial balance = 10000
Deposit = 5000
```

Expected:

```text
Final balance = 15000
```

---

### Insufficient Funds

Attempting to transfer or withdraw more than the available balance should raise:

```python
InsufficientFundsError
```

---

### Additional Unit-Test Targets

Tests should cover:

* Account creation
* Duplicate names
* Account-name validation
* Zero-balance deactivation
* Withdrawal validation
* Self-transfer rejection
* Negative amounts
* Inactive accounts
* Transaction immutability
* Enum constraints
* Balance invariants
* Transaction ID uniqueness

---

# 24. Integration Testing

## Scope

Integration tests verify interaction between:

```text
Python Objects
      ↓
Serialization
      ↓
JSON
      ↓
Deserialization
      ↓
Python Objects
```

Tests should verify:

* Financial values remain integers
* Datetimes serialize correctly
* Datetimes deserialize correctly
* Account state survives a save/load cycle
* Transactions survive a save/load cycle
* Atomic file replacement works correctly

Temporary test files should be used rather than the production ledger.

---

# 25. UI / Smoke Testing

The UI test layer simulates realistic user interaction.

`pytest`'s `monkeypatch` utility can replace:

```python
builtins.input
```

with predefined input sequences.

Example:

```python
[
    "1",
    "acc_main",
    "acc_savings",
    "100.00"
]
```

This allows tests to verify that:

* Menus transition correctly
* Invalid input is recovered from
* Transactions complete successfully
* The application does not hang
* The correct output is produced

---

# 26. Explicitly Out of Scope

The following features are excluded from the current version.

## 26.1 Multi-User Authentication

The application is single-user.

Excluded:

* Login passwords
* User accounts
* Permission levels
* Multi-user sessions

Local operating-system permissions are assumed to provide file-level protection.

---

## 26.2 Multi-Currency Conversion

Excluded:

* Multiple currencies
* Exchange-rate calculations
* Live FX APIs
* Currency conversion

The current application operates using one static currency representation.

---

## 26.3 Cloud / Network Persistence

Excluded:

* SQL servers
* Cloud databases
* Web APIs
* Remote synchronization
* Network persistence

All data remains local:

```text
data/ledger.json
```

---

## 26.4 GUI / Rich Visualization

Excluded:

* Desktop GUI
* Graphical charts
* Image generation
* Visual dashboards

Financial summaries will be displayed through:

* Text
* Structured tables
* ASCII layouts

inside the terminal.

---

# 27. Design Invariants

The following rules should remain true throughout the application's lifetime.

### Account Invariants

```text
Account IDs are unique.
Account names are unique case-insensitively.
Account balance cannot become negative.
Account ID cannot change after creation.
Account type cannot change after creation.
Created timestamp cannot change after creation.
Inactive accounts cannot receive normal transactions.
```

### Transaction Invariants

```text
Transaction IDs are unique.
Transactions are immutable after creation.
Transaction amounts cannot be negative.
Transactions reference valid accounts where required.
Transfers cannot target the same account.
Transfers must be atomic.
```

### Persistence Invariants

```text
Production ledger should never intentionally contain partially written JSON.
Financial state must survive normal application restarts.
Serialization must preserve financial precision.
```

---

# 28. Implementation Order

The design naturally breaks into the following implementation sequence:

```text
1. Domain Models
       ↓
2. Domain Exceptions
       ↓
3. Validation Rules
       ↓
4. Account Management
       ↓
5. Deposit / Withdrawal Logic
       ↓
6. Transfer Logic
       ↓
7. Transaction Immutability
       ↓
8. Persistence / JSON Serialization
       ↓
9. Atomic File Replacement
       ↓
10. Reporting & Queries
       ↓
11. CLI Menus
       ↓
12. Automated Tests
       ↓
13. Documentation
```

This keeps the financial core independent from the interface and allows the service layer to be tested before the complete CLI is built.

---

# 29. Final Review Checklist

Before implementation is considered complete, verify:

## Domain

* [ ] `Account` model finalized
* [ ] `Transaction` model finalized
* [ ] Enums finalized
* [ ] Field mutability rules finalized
* [ ] Transaction immutability implemented
* [ ] Balance invariant implemented

## Business Rules

* [ ] Account name uniqueness
* [ ] Account name length validation
* [ ] Zero-balance deactivation
* [ ] Inactive-account restrictions
* [ ] Overdraft protection
* [ ] Negative amount protection
* [ ] Self-transfer prevention
* [ ] Transaction immutability
* [ ] Transfer atomicity

## Persistence

* [ ] JSON schema finalized
* [ ] Unique transaction IDs
* [ ] Correct account references
* [ ] Datetime serialization
* [ ] Datetime deserialization
* [ ] Atomic file replacement
* [ ] Corrupted-file recovery policy finalized

## Testing

* [ ] Unit tests
* [ ] Integration tests
* [ ] UI/smoke tests
* [ ] Success paths
* [ ] Error paths
* [ ] Edge cases
* [ ] Persistence tests
* [ ] Atomicity tests

## CLI

* [ ] Main menu
* [ ] Account management
* [ ] Deposit
* [ ] Withdrawal
* [ ] Transfer
* [ ] Transaction history
* [ ] Financial reports
* [ ] Filtering
* [ ] Error messages
* [ ] Inactive-account management

## Documentation

* [ ] Installation/setup instructions
* [ ] Usage instructions
* [ ] Architecture explanation
* [ ] Data model documentation
* [ ] Business rules documented
* [ ] Testing instructions

---

# 30. Open Design Decisions

These points should be settled before or during implementation rather than being accidentally decided by the code.

### 30.1 Transaction Representation

Finalize exactly how deposits, withdrawals, and transfers populate account-reference fields.

---

### 30.2 Corrupted Ledger Recovery

Decide whether corrupted JSON should:

* Automatically reset to an empty ledger
* Be backed up/quarantined
* Require explicit user recovery
* Attempt automatic recovery

For financial data, the recovery policy should prioritize preservation of the existing ledger.

---

### 30.3 Transaction Timestamp Policy

Finalize whether:

* Users may provide historical timestamps
* Future timestamps are prohibited
* All timestamps are generated by the application
* A limited amount of timestamp adjustment is allowed

---

### 30.4 Account Status Model

Decide whether account state should remain a simple:

```python
is_active: bool
```

or become an enum such as:

```python
class AccountStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FROZEN = "frozen"
    ARCHIVED = "archived"
```

The latter should only be introduced if the additional states have meaningful behavioral differences.

---

# 31. Core Design Principle

The central architectural principle of the project is:

> **The CLI should never be responsible for financial truth.**

The system should instead follow:

```text
CLI
 ↓
Validation
 ↓
Service / Domain Logic
 ↓
Validated Domain State
 ↓
Persistence
 ↓
JSON
```

The interface can change without changing the financial rules.

The persistence mechanism can change without rewriting the CLI.

The business rules remain centralized in the service/domain layer.

That separation is what allows the project to remain maintainable as the application grows.
