| Area | Concrete evidence | Classification | Exercise that demonstrates improvement |
| --- | --- | --- | --- |
| Requirements analysis | Added account caps without requirements justification; removed manual transaction dates despite specification. | Process lapse | Extract requirements from a feature specification and produce a requirements-to-code checklist before implementation. |
| Software design | Initially struggled with where validation belongs and whether entities should be objects or dictionaries. | Knowledge gap + application gap | Given a feature, identify component responsibilities and justify where each business rule belongs. |
| Technical decision-making | Introduced pending-state machinery before establishing whether atomic writes already prevented partial transfers.	 | Process lapse |Investigate a failure scenario, identify existing guarantees, compare alternatives and justify the simplest sufficient solution. |
| Edge cases and invariants | Self-transfer prevention existed only in the UI; invalid transaction states could be constructed. | Knowledge gap + application gap | Build an invariant table and write tests attempting to violate every invariant. |
| Testing | Tests passed despite missing withdrawal account identification and incomplete serialization coverage. | Knowledge gap + process lapse | Write tests for missing fields, invalid states and failure scenarios; verify that removing validation causes tests to fail. |
| Persistence and consistency | Corrupted ledger recovery could result in valid financial data being overwritten; operation-ordering questions remained unanswered. | Knowledge gap + application gap | Reproduce corruption and save failures experimentally; document memory and disk state at each failure point. |
| Engineering discipline | Undocumented design changes, contradictory documentation and unused from_json discovered only after prompting. | Process lapse | Use a drift ledger, decision log, codebase audit and pre-submission checklist. |
| AI-assisted engineering | Some polished explanations contained stronger claims than the reasoning demonstrated. | Process lapse + application gap | Write independent technical explanations before using AI to critique them; defend every architectural claim under questioning. |



ledger.json holds 500 valid transactions and one record with a typo. The app starts, prints an error, and continues with an empty ledger. The user, not reading closely, records a ₦500 expense. What does ledger.json contain afterward?

Just the new ₦500 expense since the previous sessions were cleared due to the corrupted record