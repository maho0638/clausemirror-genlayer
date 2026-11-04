# ClauseMirror

A minimal GenLayer Intelligent Contract that compares the meaning of **two public clauses in different languages** and records a validator-reviewed structured verdict.

## What it does

- A user submits two texts with language labels.
- The submitter requests one AI review. GenLayer's nondeterministic execution independently checks the proposed verdict across validators.
- Only the exact decision (`SAME`, `DIFFERENT`, `UNCLEAR`) is stored, not a fabricated legal justification.
- Anyone can read the public record. Only the original submitter may invoke a review, and only once.

## Contract

`contracts/ClauseMirror.py` — class `ClauseMirror`

1. `submit(source_language, target_language, source_clause, target_clause)` returns a case ID.
2. `review(case_id)` returns a decision.
3. `get_case(case_id)` returns public JSON.
4. `total_cases()` returns the count.

## Example

`submit("en", "tr", "Cancellation requires 14 days notice.", "Iptal icin 7 gun onceden bildirim gerekir.")`. The likely result is `DIFFERENT`, but no specific model outcome is guaranteed.

## Limitations

This compares **user-supplied** texts. It does not verify official source documents, provide legal advice, prove correctness, or authenticate authors. Model consensus is agreement, not legal truth. All inputs are public on-chain; **never include private contracts or personal information**. No payments, escrow, browsing or autonomous actions.

## Testing

```bash
python -m pip install pytest
python -m compileall -q contracts tests
pytest -q tests
```

Unit tests use a mocked GenLayer host and do **not** establish finalized on-chain validator consensus. Verify with a compatible GenVM release before any Portal claim of live execution.

This clean rebuild intentionally excludes the old multi-service Studio/Docker CI experiments.
