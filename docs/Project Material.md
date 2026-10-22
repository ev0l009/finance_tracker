# PROJECT 1 — PERSONAL FINANCE & WALLET MANAGER

**Sprint status:** 🟢 Active  
**Developer:** You  
**Role:** Senior Engineer / Mentor — me  
**Objective:** Internalization + Principled Implementation

This is your first serious blank-project exercise.

I am deliberately **not** giving you an architecture, class list, database schema, directory structure, or implementation recipe.

---

# 1. The Client

You have been contracted to build a small personal finance application for an individual who wants to stop managing their finances through scattered notes and spreadsheets.

They have money in several places:

* a bank account
* a savings account
* cash
* potentially other wallets/accounts later

They want one application where they can understand their financial position and record what happens to their money.

The client is not a programmer.

They don't care whether you use classes, functions, JSON, SQLite, or anything else.

They care that:

> **Their financial records are correct, understandable, persistent, and usable.**

---

# 2. The Problem

The client needs to be able to answer questions such as:

> How much money do I currently have?

> How much is in my savings account?

> What did I spend money on this month?

> How much did I spend on food?

> What income did I receive in September?

> What transactions occurred between September 1 and September 15?

> I moved ₦100,000 from my bank account to savings. Did my total money change?

> How much money do I have across all my accounts?

> Can I find that ₦25,000 transaction from three weeks ago?

The application must allow them to answer these questions reliably.

---

# 3. Functional Requirements

## 3.1 Accounts

Users must be able to create and manage financial accounts.

An account should have an identifiable name.

Examples:

```text
Main Bank
Savings
Cash
Mobile Wallet
```

The system must support multiple accounts simultaneously.

Users should be able to:

* create an account
* view accounts
* inspect an account
* deactivate an account where appropriate

You must determine the precise business rules around account modification and deactivation.

---

# 3.2 Income

Users must be able to record income.

Example:

```text
Salary
₦450,000
Main Bank
September 1, 2026
```

The income must affect the relevant account's balance.

It must also become part of the user's transaction history.

---

# 3.3 Expenses

Users must be able to record expenses.

Example:

```text
Groceries
₦35,000
Food
Main Bank
September 4, 2026
```

The expense must affect the relevant account's balance.

It must become part of transaction history.

---

# 3.4 Transfers

Users must be able to move money between their own accounts.

Example:

```text
Main Bank → Savings
₦100,000
```

The system must correctly represent this as movement of existing money.

It must **not** artificially report:

```text
Income:   +₦100,000
Expense:  -₦100,000
```

The total amount of money owned by the user should remain unchanged by an internal transfer.

---

# 3.5 Transaction History

Users must be able to inspect historical financial activity.

A transaction record should provide enough information to understand:

* what happened
* when it happened
* how much money was involved
* which account was involved
* transaction type
* category where applicable
* useful descriptive information

The history must remain useful when the number of transactions becomes large.

---

# 3.6 Searching and Filtering

Users need to find relevant transactions.

The application must support filtering by appropriate criteria including:

* date
* date range
* transaction type
* account
* category
* minimum amount
* maximum amount

The user should be able to combine filters.

For example:

> Find expenses from Main Bank between September 1 and September 15 that were at least ₦20,000.

You must decide how the application behaves when no results match.

---

# 3.7 Balances

Users must be able to determine:

* an individual account balance
* their total balance across accounts

Example:

```text
Main Bank     ₦500,000
Savings       ₦200,000
Cash           ₦50,000
-----------------------
Total         ₦750,000
```

The figures must remain internally consistent.

---

# 3.8 Financial Reports

The application must provide useful summaries over a selected period.

At minimum, users should be able to determine:

* total income
* total expenses
* net change
* spending by category
* activity by account

Transfers should not distort income and expense reporting.

---

# 4. Validation & Business Rules

The application must reject invalid operations.

At minimum, consider:

### Monetary values

* zero amounts
* negative amounts
* invalid numeric input
* extremely large values
* precision issues

### Accounts

* nonexistent accounts
* duplicate accounts
* inactive accounts
* invalid account references

### Transfers

* same source and destination
* insufficient funds
* invalid amount
* nonexistent source
* nonexistent destination
* inactive accounts

### Dates

* malformed dates
* invalid calendar dates
* future dates

**Important:**

Some of these requirements deliberately contain business-rule ambiguity.

For example:

> Should future transactions be allowed?

There is no predefined answer.

You are expected to make a reasonable engineering/product decision, document it, and test it.

---

# 5. Persistence

The application must persist financial data.

If the user:

1. creates accounts,
2. records transactions,
3. closes the application,
4. starts it again,

their information must still exist.

The application is initially local.

There is no requirement for:

* cloud synchronization
* authentication
* networking
* banking APIs
* multi-user support

You must choose the persistence strategy.

Your choice needs to be justified.

---

# 6. Reliability Requirement

Financial operations must preserve consistent state.

Consider:

```text
Transfer ₦100,000
Account A → Account B
```

What happens if part of the operation succeeds and another part fails?

You don't need enterprise distributed systems.

But your design should demonstrate that you have thought about **atomicity and data integrity**.

---

# 7. User Interface

The first release must have a usable CLI.

The application should provide understandable workflows for:

* account management
* recording transactions
* transfers
* viewing balances
* transaction history
* searching/filtering
* reports

The user should not need to know Python to operate the application.

A GUI is **not required for v1**.

We will decide later whether Project 1 benefits sufficiently from one.

---

# 8. Error Handling

Normal user mistakes should not produce ugly application crashes.

For example, entering an invalid amount should result in useful feedback rather than an unexplained traceback.

However:

> **Do not solve this by catching `Exception` everywhere.**

Failures should be handled at sensible boundaries.

Unexpected programming errors should not be silently swallowed.

---

# 9. Testing

The project must have an automated test suite.

It should demonstrate confidence in:

### Core behavior

* account management
* income
* expenses
* transfers
* balances
* transaction history
* filtering
* reporting
* persistence

### Invalid behavior

* invalid amounts
* invalid accounts
* insufficient funds
* invalid transfers
* invalid dates
* other relevant validation failures

### Edge cases

You are responsible for identifying additional edge cases.

Do not limit your tests to the examples given in this specification.

---

# 10. Documentation

The project must include a useful README.

It should explain:

* what the application does
* how to install it
* how to run it
* how to run tests
* how persistence works
* important assumptions
* known limitations

Important public behavior should also be appropriately documented in the code.

---

# 11. Constraints

For the initial release:

### Required

* Python
* automated tests
* static typing
* persistent data
* CLI
* documentation

### Not required

* authentication
* cloud services
* networking
* external banking APIs
* multi-user support
* machine learning
* web deployment
* complex infrastructure

### Engineering principle

Don't introduce technology simply because you know it exists.

Every dependency and major architectural decision should have a reason.

---

# 12. Acceptance Criteria

The project cannot be considered complete until:

### Functionality

* [ ] Multiple accounts work.
* [ ] Income can be recorded.
* [ ] Expenses can be recorded.
* [ ] Transfers work correctly.
* [ ] Balances are correct.
* [ ] Total balance is correct.
* [ ] Transaction history works.
* [ ] Search/filtering works.
* [ ] Reports work.
* [ ] Data survives application restart.

### Reliability

* [ ] Invalid operations are rejected.
* [ ] User input errors are handled appropriately.
* [ ] Financial state cannot easily become inconsistent through normal operations.
* [ ] Transfers preserve correct financial state.

### Engineering

* [ ] Appropriate architecture.
* [ ] Sensible responsibility boundaries.
* [ ] Appropriate typing.
* [ ] Appropriate exception handling.
* [ ] Automated tests.
* [ ] Useful documentation.
* [ ] Maintainable code.
* [ ] No significant unnecessary complexity.

### User Experience

* [ ] The CLI is understandable.
* [ ] Normal workflows are reasonably convenient.
* [ ] Errors are understandable.
* [ ] The application gives useful feedback.

---

# 13. Sprint Milestones

We're going to use **five gates**.

## GATE 1 — Requirements & Design

Before implementation.

You will submit:

* requirements interpretation
* assumptions
* identified ambiguities
* business rules you've chosen
* architecture proposal
* project structure
* data model
* persistence decision
* error-handling strategy
* testing strategy
* explicit out-of-scope decisions

### Assessment

Your external reviewer must determine whether your design is:

* coherent
* appropriately scoped
* internally consistent
* testable
* maintainable
* appropriately simple

**Do not begin serious implementation until this gate is passed.**

---

# GATE 2 — Core Application

Build the fundamental financial operations.

At minimum:

* accounts
* income
* expenses
* transfers
* balances
* persistence

### Submission

Provide:

* source code
* tests
* test results
* current README
* any relevant design changes

### Assessment

The reviewer evaluates:

* correctness
* architecture
* domain modeling
* state consistency
* error handling
* typing
* testing quality

---

# GATE 3 — Query & Reporting

Add:

* transaction history
* filtering
* searching
* reports
* useful summaries

### Assessment

Particular attention should go toward:

* query design
* correctness
* edge cases
* test quality
* separation of responsibilities
* usability

---

# GATE 4 — Release Candidate

The application should now feel like an actual product.

Review:

* CLI usability
* validation
* error messages
* persistence reliability
* documentation
* test coverage
* code quality
* consistency

Fix significant issues discovered during this phase.

---

# GATE 5 — Final Engineering Review

This is the serious assessment.

The reviewer evaluates the entire project across:

| Area            | Required                       |
| --------------- | ------------------------------ |
| Requirements    | Full compliance                |
| Functionality   | Correct behavior               |
| Architecture    | Appropriate design             |
| Domain modeling | Sound representation           |
| Error handling  | Deliberate and reliable        |
| Typing          | Accurate and useful            |
| Testing         | Meaningful behavioral coverage |
| Persistence     | Reliable                       |
| Documentation   | Developer/user usable          |
| CLI             | Reasonably usable              |
| Maintainability | Appropriate for scope          |
| Complexity      | Justified                      |
| Code quality    | Professional standard          |

The reviewer should identify:

* critical issues
* major issues
* moderate issues
* minor issues
* technical debt
* strengths
* recurring weaknesses
* areas requiring remediation

---

# 14. Assessment Submission Protocol

For each gate, **do not just say "review my project."**

Use the master assessment prompt we established earlier and append the relevant gate's requirements.

Your submission should contain whatever artifacts the gate specifies.

The external reviewer should iteratively challenge you:

> Finding → Your reasoning → Hint → Your change → Re-review

rather than simply dumping the answers on you.

---

# 15. Assessment Debrief

After you've passed a gate, bring the **assessment history** back here.

I want to know:

* what the reviewer found
* what you initially got wrong
* what you struggled to understand
* how many iterations something required
* what eventually clicked
* what you fixed
* what remains weak
* what the reviewer identified as recurring behavior

Especially preserve cases where you initially defended a decision and later changed your mind.

That's valuable engineering-learning data.

---

# 16. Definition of Done

Project 1 is **not done** when:

```text
"Everything works."
```

It is done when you can reasonably demonstrate:

> **I can explain what I built, why I designed it this way, demonstrate that it works, explain how it fails, show how I tested it, maintain it, and defend the important engineering decisions.**

And the independent assessment agrees that the remaining issues are reasonable for the scope.

---

# 17. Your First Deliverable

**Stop here.**

Do not start implementing yet.

Your immediate task is **Gate 1 — Requirements & Design**.

Prepare your Engineering Design Submission.

I am intentionally not giving you:

* classes
* functions
* modules
* database schema
* directory tree
* design patterns
* persistence implementation
* CLI architecture

Those are yours.

Once your design is ready, **do not paste it here for me to approve**.

Take it through the external assessment workflow using the assessment prompt we've established.

Then bring the **assessment debrief and review history** back here.

I'll use that to determine what we challenge next.

**The project has officially begun.**
