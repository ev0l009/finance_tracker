Design Choice Note: Replaced a traditional nested while-loop logic with a simplified State Pattern (MenuState Enum). This decouples individual menu features from the orchestrator, eliminates raw string literal bugs, and ensures that adding a new menu option only requires mapping a new enum state.

*   **Constraint-Based Routing over Open Input:** To drastically reduce runtime exception vectors, the interface replaces traditional open-ended text prompts with dynamically generated, bounded selection menus (e.g., during account inspection, target fund routing, or expense categorization). This defensive design choice:
    *   Completely eliminates semantic bugs caused by user spelling typos, case mismatches, or trailing whitespaces.
    *   Guarantees that actions can only be executed against valid, currently active structural entities.
    *   Drastically reduces processing overhead by shifting verification filters from post-input data parsing loops down into the presentation delivery layer.

*   **Progressive Architecture (Simplicity to Reusability):** Developed with an iterative design philosophy—prioritizing minimal, working foundations first, then systematically refactoring for modular reusability. This calculated approach:
    *   Completely avoids premature optimization and unnecessary abstractions.
    *   Keeps the execution pipeline clean, scannable, and highly maintainable.
    *   Ensures that every component added serves a direct, structural purpose without introducing feature creep.

*   **Rich Domain Modeling (High Cohesion):** Reduced the structural footprint of the orchestrating `Tracker` engine by delegating account lifecycle operations directly into the `Account` module. 
    *   Ensures that individual data entities remain autonomous and govern their own business invariants.
    *   Maximizes class cohesion by keeping data and the operations that mutate that data in the exact same module boundaries.
