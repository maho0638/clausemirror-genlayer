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

```bash
# Dependency-free contract logic tests with a deliberately small GenLayer runtime stub:
python -m pytest tests/test_contract.py -q
# Official direct SDK tests (requires genlayer-test):
python -m pytest tests/test_direct_sdk.py -q
python -m compileall -q contracts tests

# Official linter and SDK schema validation (requires internet and packages):
python -m pip install genvm-linter
# These commands were NOT executable in the offline preparation environment:
genvm-lint check contracts/ClauseMirror.py
genvm-lint schema contracts/ClauseMirror.py --output abi.json

# In a GenLayer Studio environment, deploy and run an actual accepted
# multi-validator review and a deliberately disputed review.
# Do NOT treat the stub suite as onchain or GenVM validation.
```

The pure-Python test stub checks authorization, immutability, input validation, controlled outcomes, and disagreement rollback **but does not prove GenVM compatibility, actual consensus, fee behavior, storage serialization, or public-network deployment**. Do not market this as audited or production-ready until real toolchain checks and a Studio multi-validator transaction pass. See [VERIFICATION.md](VERIFICATION.md).

## Technical references

- GenLayer [equivalence principle](https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle)
- GenLayer [storage reference](https://docs.genlayer.com/developers/intelligent-contracts/features/storage)
- GenLayer [testing guide](https://docs.genlayer.com/developers/intelligent-contracts/testing)

License: MIT. Contributions welcome with reproducible tests and a clear explanation of security impact.


## Release gate (3 November 2026)

The initial prototype was hardened to use official `response_format="json"` for GenLayer LLM calls. This revision migrates to SDK 0.3: `import genlayer as gl`, `gl.contract.Contract`, `gl.storage.TreeMap`, and `gl.vm.run_nondet`. The contract validates the LLM dictionary strictly, rejects malformed leader and validator responses, and rejects unpaired Unicode surrogates, dangerous control characters and bidi override controls. The stub suite includes 75 sequential independent cases and cross-language Unicode coverage. The CI workflow now also runs official `genlayer-test` direct-mode tests, whose status must be checked in GitHub Actions.

**This is still not a verified Studio deployment.** The preparation environment has no installed official `genvm-linter`, `genlayer-test`, CLI, or Docker, and package installation cannot reach PyPI (DNS/network denied). The GitHub Actions workflow includes the official linter gate but it has not yet run. A true GenVM/Studio run is mandatory before claiming deployment readiness. No GitHub push or chain transaction has been performed.