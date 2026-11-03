You’ve made four real decisions or deferrals since Batch 1 began. Each is a log entry in your Decision/Why/Alternatives/Why rejected/Consequences format:


Reversal from automatic timestamps to manual dates.
Status as an Enum or a bool, with your actual reason.
NullEligibleAccountsError: keep, move, or remove.
Self-transfer prevention deferred, recorded as a known gap.

transactions
transaction_type is a plain overridable str. What stops a transfer labelled “deposit”?
Who should turn a bad stored record into a meaningful error instead of a raw KeyError?
Find two more bugs that survive the current test suite, besides the missing timestamp in to_dict.
How will tests control “now” once future dates are rejected?



## Chat Summary – Flags Raised and Points to Fix

The review identified several design inconsistencies and potential bugs across the Finance Tracker. The main recurring concern is that implementation decisions have drifted from the approved Gate 1 design without being documented.

### 1\. Exception hierarchy (`exceptions.py`)

**Flags raised:**

- Unintentional changes to the approved exception hierarchy.
- `AccNameError` overlaps with `DuplicateAccountNameError`.
- `InvalidOptionError` is a UI concern rather than a domain exception.
- `NullEligibleAccountsError` may represent a normal empty result rather than an exceptional condition.
- `InvalidAccountTypeError` primarily concerns invalid persisted data.
- `AccStatusError` and `InvalidAccountStatusError` introduce status concepts that need clearer justification.
- `InvalidAmountError` combines several errors that were previously separate.

**Points to fix:**

- Reconcile the current exceptions against the original Gate 1 design.
- Restore `DuplicateAccountNameError` as a separate, specific exception.
- Remove the stale reference to reserved account names if no such rule exists.
- Decide whether empty account collections warrant exceptions.
- Clarify where persistence-related exceptions belong.
- Standardise exception naming (preferably the `Error` suffix).
- Document all intentional design changes.

### 2\. Transaction dates and timestamps

**Major flag:**

- Automatic timestamps replaced manual transaction dates, potentially removing functionality required by the original specification.

**Points to fix:**

- Decide whether users should record transactions that happened on previous dates.
- If automatic timestamps remain, make time controllable in tests.
- Clarify whether date validation belongs in the model or storage layer.
- Resolve the inconsistency of accepting `datetime | str` in the transaction model when storage is responsible for parsing dates.
- Document the revised time-handling design.

### 3\. Transaction model and invariants

**Flags raised:**

- Withdrawal transactions initially lacked an account identifier.
- Self-transfer prevention appeared to exist only in the UI.
- `transaction_type` is a plain, overridable string.
- Potential inconsistencies between transaction creation and loading stored transactions.

**Points to fix:**

- Add `acc_id` to `WithdrawalTrx` (a correction already proposed).
- Ensure transaction types cannot contradict their respective transaction classes.
- Enforce self-transfer prevention in the service/model layer, not just through UI selections.
- Identify which transaction invariants the object itself can enforce.
- Separate new transaction creation from stored transaction reconstruction.
- Ensure malformed stored records produce meaningful exceptions rather than raw `KeyError` exceptions.

### 4\. Persistence and data integrity

**Major outstanding concern:**

- The original design allows a corrupted `ledger.json` to be replaced with an empty baseline.

This could result in permanent loss of the original ledger when the application next saves.

**Points to fix:**

- Reconsider automatic replacement of corrupted ledger files.
- Preserve or back up the original file before attempting recovery.
- Introduce meaningful persistence-specific exceptions.
- Review validation when loading stored records.

### 5\. Testing and quality assurance

**Outstanding items:**

- Identify two additional bugs that survive the current test suite, besides the missing timestamp in `to_dict`.
- Test transaction invariants independently of UI behaviour.
- Test malformed and incomplete JSON records.
- Ensure tests can control the current time.
- Submit `models.py`, its corresponding tests, and pytest output for review.

### 6\. Development process improvements

A recurring weakness identified throughout the review is **design drift**: implementation decisions are being made during coding without being reconciled with the original specification.

Recommended improvements:

- Maintain a **Design Drift Ledger** documenting original requirements, current implementation and reasons for changes.
- Maintain a **Spec-to-Code Checklist** for every validation requirement.
- Record design deviations in the Engineering Decision Log as soon as they occur.
- Distinguish between UI conveniences and actual domain-level enforcement.

---

### Priority order

| Priority | Action |
| --- | --- |
| Critical | Reconsider corrupted ledger recovery and potential data loss. |
| High | Fix transaction account identification and enforce transaction invariants. |
| High | Resolve transaction date/timestamp design. |
| High | Separate creation validation from persistence loading. |
| Medium | Reconcile and clean up the exception hierarchy. |
| Medium | Investigate additional bugs missed by existing tests. |
| Medium | Improve design-change documentation and testing discipline. |

**Current position:** The withdrawal account identifier omission has been acknowledged as a genuine bug, with a correction proposed. However, the remaining transaction-model questions (Q2, Q4 and timestamp ownership) are still unanswered.

**Overall takeaway:** The biggest issue isn't necessarily the individual coding mistakes. It's ensuring that the implementation consistently enforces the approved design, that important rules cannot be bypassed by other callers, and that deviations are deliberate and documented.