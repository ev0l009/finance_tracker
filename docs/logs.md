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