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


Your prediction

The core of it is right: the original data is lost. But the prediction has two problems, and noticing them before running anything is exactly what the prediction step is for.

1. It doesn’t say when the data is lost. You wrote that the sessions were “cleared due to the corrupted record.” Think about the file on disk at the moment the load fails. Has anything changed it yet? Then ask what triggers the first write, and whether your app ever saves without a user operation (on exit, say). Add that to the prediction.

2. It contradicts your own rules. You predicted the file would hold “just the new ₦500 expense.” After an empty-baseline recovery, what exists in the ledger? Given your rules (an expense must reference an account, balances can’t go negative), what would have to happen before a ₦500 expense could be recorded? Work out the full sequence of actions and what the file holds after each.

I’d tag this one an application gap: you know an expense needs an account with enough money, and that dependency didn’t get applied while you were predicting. That’s the recognition step we discussed.

Next
Send your revised prediction as a short list of “after this action, the file contains X” steps. Do this before running anything.
Then run it: copy your ledger first, corrupt one record, and follow your own sequence.
Report the result, and note any place where it differed from your prediction.
Start Stage 1 alongside it. Confirm or adjust the day split.


ledger.json holds 500 valid transactions and one record with a typo. The app starts, prints an error, and continues with an empty ledger. The user, not reading closely, records a ₦500 expense. What does ledger.json contain afterward?

I'll try again with focus on transaction records. The app tries to load stored records from ledger.json, assuming there are no errors while reading from ledger.json, during deserialization, each trx dict is rebuilt as an object. Say the field with the typo is transaction_type, this particuar record raises an error which will crash the app. i didn't make any provisions for this scenario during loading or in the storage layer. I think this is not necessarily a bad thing as all records aren't wiped yet, including the corrupt one. I haven't tested yet. just tried testinmg this scenario yet. Keep pointing me in the right direction if i haven't gotten it tho

| Scenario | User sees at startup | File contents right after startup | Does anything save on the way out? |
| --- | --- | --- | --- |
| Syntax error in the file, today’s code | Crash since its a syntax error, json decode exception will be triggered which i handled by raising the error and returning a fresh session | Same current corrupt file with the syntax error | A fresh session that overwrites the previously  corrupt data |			
| Bad value in one record, today’s code | This will crash(fail fast). When the account object checks the corrupt field it'll raises an `InvalidTransactionTypeError` | Nothing changes | The same file stays as is |			
| Bad value in one record, after option A | The syntax error crashes the app so the bad value is never read | Same current corrupt file with syntax error and value error | A fresh session overwriting the previously corrupt session  |	