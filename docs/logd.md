Design Choice Note: Replaced a traditional nested while-loop logic with a simplified State Pattern (MenuState Enum). This decouples individual menu features from the orchestrator, eliminates raw string literal bugs, and ensures that adding a new menu option only requires mapping a new enum state.

*   **Constraint-Based Routing over Open Input:** To drastically reduce runtime exception vectors, the interface replaces traditional open-ended text prompts with dynamically generated, bounded selection menus (e.g., during account inspection, target fund routing, or expense categorization). This defensive design choice:
    *   Completely eliminates semantic bugs caused by user spelling typos, case mismatches, or trailing whitespaces.
    *   Guarantees that actions can only be executed against valid, currently active structural entities.
    *   Drastically reduces processing overhead by shifting verification filters from post-input data parsing loops down into the presentation delivery layer.
