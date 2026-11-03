# Verification status and release gates

| Gate | Status | Evidence |
| --- | --- | --- |
| Source syntax | automated locally | `compileall` |
| Auth, state transitions, adversarial text, independent decision-check logic | automated locally | `pytest tests/`: 57 passing with runtime stub (2026-11-03) |
| GenVM linter | **NOT RUN** | `genvm-lint` unavailable locally; PyPI unreachable (DNS) |
| Real `genlayer-test` direct execution | **NOT RUN** | `genlayer-test` unavailable locally; PyPI unreachable (DNS) |
| Studio multi-validator consensus & revert | **NOT RUN** | no running Studio/real validators |
| Onchain gas cost and limits | **NOT RUN** | no testnet deployment |
| Security audit / formal verification | **NOT DONE** | third-party independent review needed |

`pytest`'s fake `run_nondet_unsafe` is *not* GenLayer consensus. It only verifies the program's control flow with deterministic scripted model responses. Never interpret the green tests as onchain proof.

## Required before Portal submission

1. Pin/verify compatible GenVM runner, `genlayer-test` and linter versions.
2. Run `genvm-lint check contracts/ClauseMirror.py`; resolve all findings.
3. Run real GenLayer direct-VM tests, including expected rejects and storage types.
4. Deploy on Studio with test accounts; verify authorized review, unauthorized rejection, validator agreement/disagreement, finality and receipt retrieval.
5. Test two different LLM providers / models with EN/TR material and non-material changes, including deliberately ambiguous clauses.
6. Inspect receipt JSON and demonstrate that `note_verified` never wrongly claims rationale validation.
7. Review on-chain input privacy, cost, supported Unicode, and replay/revision behavior.
8. Only then ask the user before Portal submission, mainnet deployment or spending funds.


## Improvements since v0.1.0

- Replaced raw-text `gl.nondet.exec_prompt(...)` with official `response_format="json"`.
- Validates exact dictionary keys, types, bounded notes and serialized size for both leader and validator.
- Invalid validator output returns a negative vote rather than accidentally approving a malformed leader response.
- Rejects C0/C1 controls (excluding newlines/tabs), unpaired Unicode surrogate values, and bidi override/isolate characters before trimming input; permits genuine Turkish/Arabic script.
- Added adversarial tests, invalid leader bypass checks, validator malformed-output checks, and a 75-case persistence stress test.
- Added an official `genvm-lint check` gate to the CI workflow for future GitHub updates (not yet run).

## Blocking issues

This build is **not a claim of 100% technical correctness**. A genuine GenVM deployment and multi-validator acceptance/disagreement test cannot be emulated by Python stubs. Network access and Docker are unavailable in the current environment. Do not submit this as an already-tested GenVM contract; first run the official linter, a direct-VM SDK test, and real Studio deployment + consensus test. LLM consensus is not mathematical proof of legal translation accuracy.

## 3 November SDK migration

Target SDK reference: [v0.3.0-rc10](https://sdk.genlayer.com/main/_static/ai/api.txt). Migrated the imports, contract base class, persistent storage type, the custom nondeterminism comparison API, and removed callable `u32(...)` casts (no longer supported in SDK 0.3). CI includes the official GenVM linter and GenLayer Direct Mode suite; check Actions for their actual outcomes before asserting them as passed. Full Studio consensus is not covered by Direct Mode.