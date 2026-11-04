# Portal submission — ClauseMirror

**Category:** Developer / Intelligent Contracts

**Title:** ClauseMirror — Bilingual Clause Meaning Consensus

**Notes (under 1,000 characters):**

ClauseMirror is a reusable GenLayer Intelligent Contract for comparing the operative meaning of public clauses written in two different languages. The author submits both clauses, and the contract requests an AI judgment: SAME, DIFFERENT, or UNCLEAR. Each validator independently re-evaluates the same user-supplied text; a mismatched decisive verdict is rejected instead of stored. Immutable public records, author-only one-time review, bounded inputs, strict AI result schemas, and safe nondeterministic execution make the comparison transparent and replay-resistant. CI verified 3 logic tests, 3 official GenLayer Direct SDK tests (including positive/negative validator simulation), GenVM lint, and semantic validation. Direct tests are in-process, not live network finality. This is not legal advice or proof of document authenticity.

**Evidence URLs** (paste each into a separate URL entry):

1. Code: https://github.com/maho0638/clausemirror-genlayer/blob/rebuild/simple-clausemirror-20261104/contracts/ClauseMirror.py
2. Repository and review: https://github.com/maho0638/clausemirror-genlayer/pull/10
3. Official SDK + GenVM CI: https://github.com/maho0638/clausemirror-genlayer/actions/runs/41823445956
4. Source unit tests: https://github.com/maho0638/clausemirror-genlayer/blob/rebuild/simple-clausemirror-20261104/tests/test_direct_sdk.py

**Verification boundary:** Official Direct Mode exercises GenLayer SDK deployment/storage/validator callbacks in-process. It is not a finalized live GenVM consensus transaction or a signed on-chain explorer receipt. Do not claim live deployment.

**Deployment:** No public deploy, gas payment, or Portal submission was made.
