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
