📝 Summary (TL;DR)

Refactored a legacy tracking engine into a highly cohesive, defensive system by introducing an Enum-driven State Pattern, rich domain modeling, and constraint-based UI menus to entirely eliminate user input exceptions and runtime parsing overhead.

🛠️ Architecture & Design Patterns
 
• State Pattern Over Nested Loops: Replaced traditional nested while-loop logic with a simplified MenuState Enum.
	• Decouples individual menu features from the orchestrator.
	• Eliminates raw string literal bugs.
	• Ensures adding a new menu option only requires mapping a new enum state.
• Rich Domain Modeling (High Cohesion): Reduced the structural footprint of the orchestrating Tracker engine by delegating account lifecycle operations directly into the Account module.
	• Ensures individual data entities remain autonomous and govern their own business invariants.
	• Maximizes class cohesion by keeping data and the operations mutating that data within the same module boundaries.
• Progressive Architecture: Implemented an iterative design philosophy that prioritizes minimal, working foundations before systematically refactoring for modular reusability.
	• Avoids premature optimization and unnecessary abstractions.
	• Keeps the execution pipeline clean, scannable, and highly maintainable.
	• Ensures every added component serves a direct, structural purpose without introducing feature creep.

🛡️ User Interface & Defensive Design

• Constraint-Based Routing Over Open Input: Replaced traditional open-ended text prompts with dynamically generated, bounded selection menus (e.g., during account inspection, target fund routing, or expense categorization).
	• Eliminates semantic bugs caused by typos, case mismatches, or trailing whitespaces.
	• Guarantees actions only execute against valid, currently active structural entities.
	• Reduces processing overhead by shifting verification filters from post-input data parsing loops down into the presentation delivery layer.

Choosing to keep transactions and accounts as objects in memory on load and dicts on save. 
1. Guaranteed Data Integrity (Invariants Cannot Be Broken)

If transactions are plain dictionaries, any part of your codebase can accidentally alter them (e.g., tx["amount"] = -50). By using a frozen object with validation in __post_init__, you create a foolproof safety guarantee:
• Validation at Entry: A transaction cannot even exist in memory unless it is valid.
• Immutability: Once created, it cannot be modified by buggy code later in the execution flow. It represents an unalterable historical fact, which is exactly how a ledger should behave.

2. Separation of Concerns (Domain Logic vs. Storage Media)

• In Memory: You want a rich developer experience with type hints, dot-notation access (tx.amount), auto-completion, and business logic validation rules.
• In Storage: Databases (like MongoDB, PostgreSQL JSONB, or Redis) don't understand Python objects; they understand serialized text, JSON, or key-value structures.
• The Justification: Turning objects into dicts on save, and dicts back into objects on load, decouples your business rules from your database structure. If you change your database provider tomorrow, your transaction validation logic remains completely untouched.

3. Clear Boundaries for Time-of-Load Validation

Data in a database can occasionally become corrupted, altered by direct database scripts, or desynchronized during system migrations.
• By converting a stored dict back into a frozen object when loading it, the data is forced through __post_init__ validation again.
• This ensures that your application catches any invalid, corrupted, or backdated entries the exact second they are pulled from storage, preventing bad data from poisoning the rest of your system memory.

4. Self-Documenting Code & Type Safety

Using objects lets you leverage Python static type checkers (like mypy) and IDE autocompletion. Instead of guessing if a dictionary contains "tx_time", "timestamp", or "date", a frozen data class explicitly defines the type contract:




Q1 => A. Summary: Frozen Objects vs. Storage Dicts
In Memory (Frozen Object): Ensures absolute data integrity. Transactions cannot be created with invalid data and cannot be modified after creation, treating ledger history as unalterable. It also grants full type safety and auto-complete in your code.
In Storage (Raw Dictionary): Keeps data structures simple and lightweight. Databases natively store and query JSON or key-value structures, completely decoupling database tools from application-specific Python logic.
On Load (Dict to Object): Acts as a dynamic security checkpoint. Forcing retrieved database data back into a frozen object instantly re-runs validation, catching any corrupted or unauthorized data changes before they enter memory.
Core Justification: Dictionaries are used for simple storage compatibility, while frozen objects are used to guarantee strict, un-breachable business logic while the application is running. I have logged this

Q2/Q3:
| Field | Illegal values | Exception |
| :--- | :--- | :--- |
| `id`, `source_acc_id`,`target_acc_id`, `acc_id`  (for accounts and transactions) | empty string | `InvalidIDError` |
| `acc_name` | empty strings, string with less than 4 characters | `AccNameError` |
| `acc_type` | empty strings, invalid account type | `InvalidAccountTypeError` |
| `acc_status` | empty strings, invalid account status | `InvalidAccountStatusError` |
| `amount` | zero and negative amounts, non-integer values | `InvalidAmountError` |
| `amount` | amount greater than available balance | `ExcessDebitError` |
| `balance` | negative balance | `InvalidAmountError` |
|  `source_acc_id`,`target_acc_id` | `source_acc_id == target_acc_id` during transfers  | `SameAccountTransferError` |
| `timestamp` | empty/invalid date inputs | `InvalidTransactionDateError` |
| `transaction_type` | empty strings, invalid transaction type | `InvalidTransactionTypeError` |
| `category` | empty strings, invalid category | `InvalidCategoryError` | 
For the time entries, to reduce errors, i intend to continuously prompt the user in this order;
year, month, date, hour, minute. I'll use the 24 hour clock. The entries pass through a time patcher that parses it into this format YYYY/MM/DD​. Something close to what the datetime module can work with. The time patcher will handle validation and time processing. It will be in the ui layer somewhat, then the deeper transaction class level validation. I don't think the time should be UTC aware