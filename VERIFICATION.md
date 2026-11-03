# ClauseMirror — Multilingual Contract & Policy Consistency Receipts

**GenLayer Intelligent Contract** that compares the operative meaning of a clause in two different languages, obtains independent validator agreement on the *decision*, and records an immutable, revision-linked review receipt.

## Why this exists

Two versions of terms can look similar but materially change obligations, payment dates, exclusions, liability caps, or rights. ClauseMirror compares **specific clauses**, not whole legal documents. A user submits the exact source and target passages (and optional context), asks GenLayer validators for a structured finding, and can submit a revised target clause as a *new* linked case; the original result stays visible.

It is distinct from general evidence verification, license compliance, tender adjudication, and agent mandates: its domain is **cross-language semantic drift in obligations**.

## Contract API

Contract: `contracts/ClauseMirror.py` — class `ClauseMirror`.

| Method | Access | Behavior |
| --- | --- | --- |
| `submit_pair(source_language, target_language, source_clause, target_clause, context)` | write | Creates an immutable public case; returns its integer ID |
| `review(case_id)` | author-only write | Calls an LLM for a structured decision and has validators independently assess the same submitted passages; records result only if consensus accepts |
| `revise_target(parent_id, revised_target_clause)` | author-only write | Creates a separate pending case linked to a previously reviewed case, preserving source/context |
| `get_case(case_id)` | view | Returns the full JSON data and receipt |
| `get_author(case_id)` | view | Returns submitter address |
| `get_total_cases()` | view | Returns count |

### Outcomes

* `EQUIVALENT` — meaning and material rights/duties align.
* `MATERIAL_DIFFERENCE` — at least one operative difference detected.
* `INCONCLUSIVE` — ambiguity or insufficient context; no unwarranted pass.

The `leader_note` is **NOT** independently consensus-verified. It is a human-readable, leader-authored rationale. `note_verified=false` is intentionally recorded, while the verdict is the field checked through an independent validator execution. Human legal review is still required for high-stakes use.

## Safety / threat model

* **Every input and output is public blockchain data. NEVER submit personal data, confidential agreements, or trade secrets.**
* No payments, transfers, escrow, external writes, token staking, admin override, or third-party scraping.
* Only the original author can invoke paid AI review or create a revision; other users can read public receipts.
* Submitted source and target text cannot be edited. Revisions are new, parent-linked cases; review cannot be repeated on the same case.
* Strict per-field size limits, UTF-8/control-character checks, and controlled three-value decisions; malformed AI output or validator disagreement aborts the transaction.
* A validator **re-runs the same source-grounded task** rather than accepting a well-formatted leader claim. An LLM can still be wrong, and validators may share biases; agreement is not proof of legal equivalence.
* User-provided clauses are explicitly treated as untrusted data in the prompt. This does not mathematically eliminate prompt injection.
* No authenticity claim: the user supplies all text. No guarantee that supplied clauses match a real authoritative publication. Documents can change over time; the original snapshot remains static.
* Language tags use a conservative ASCII BCP47-like subset, not complete BCP47 parsing.

## Quick start

1. Install a matching **GenLayer Studio / CLI** and compatible GenVM runner. The `Depends` header targets the current `py-genlayer` runner listed in the official SDK reference on 3 November 2026 (v0.3.0-rc10). Recheck before deployment.
2. Open `contracts/ClauseMirror.py` in Studio and deploy with **zero constructor arguments**.
3. Submit two short, *public* clauses in different languages with `submit_pair`.
4. As the original submitter, call `review(case_id)` and wait for accepted validator consensus/finality.
5. Read `get_case(case_id)`. If a difference is found, submit a corrected target via `revise_target`; review its new case ID.

Example with expected semantics: [examples/example_en_tr.md](examples/example_en_tr.md).

## Development / verification

The repository's GitHub Actions verification uses Python 3.12 and three independent jobs:

```bash
# 65 deterministic test cases (mock GenLayer runtime and SDK 0.3 safety regressions)
python -m pytest tests/test_contract.py tests/test_sdk_api_regressions.py -q

# 4 actual GenLayer SDK Direct Mode test cases (GenLayer test framework required)
python -m pytest tests/test_direct_sdk.py -q

# GenVM lint and SDK semantic analysis (GenVM linter required)
python scripts/compat_linter_sdk03.py
 genvm-lint lint contracts/ClauseMirror.py
 genvm-lint validate contracts/ClauseMirror.py
```

The compatibility script only makes GenVM Linter 0.11.1rc2 recognize the **safe** SDK 0.3 `run_nondet_default` entry point; no rules are disabled. Direct Mode tests use the actual SDK but a mocked LLM, not public GenLayer validator infrastructure. See [VERIFICATION.md](VERIFICATION.md) for observed CI results.

### Security and release limits

Source review and official SDK Direct Mode tests cannot prove universal correctness or real-network finality. Before handling valuable or confidential data, conduct a separate Studio/testnet multi-validator integration test. The contract records public data permanently; do not upload confidential terms or personal data. Decision agreement does not independently verify the leader's explanation or the legal validity of a clause.

## Technical references

- GenLayer [equivalence principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- GenLayer [storage reference](https://docs.genlayer.com/developers/intelligent-contracts/features/storage)
- GenLayer [testing guide](https://docs.genlayer.com/developers/intelligent-contracts/testing)

License: MIT. Contributions welcome with reproducible tests and a clear explanation of security impact.


## Build status — 3 November 2026

GitHub repository: https://github.com/maho0638/clausemirror-genlayer

The SDK 0.3 implementation uses `gl.vm.run_nondet_default` for sandboxed validator consensus and the SDK-supported `gl.storage.inmem_allocate` for persistent `TreeMap` members. 65 deterministic tests and four GenLayer Direct Mode tests pass, including write authorization, stored receipts, independent validator agreement/disagreement, immutable revision links, and hostile Unicode rejection. GenVM static/safety lint and SDK semantic validation run in CI using the documented SDK 0.3 compatibility shim.

See https://github.com/maho0638/clausemirror-genlayer/actions/runs/41705418625 and [VERIFICATION.md](VERIFICATION.md) for the exact verification boundary. **No Studio/testnet multi-validator deployment or public-network finality is claimed.**