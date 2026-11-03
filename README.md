# ClauseMirror — Verification record (2026-11-03)

## Executed checks

| Check | Observed outcome | Evidence |
|---|---|---|
| Python syntax | PASS | GitHub Actions compileall |
| Deterministic authorization, state, Unicode, malformed-model, SDK safety regression tests | **65 passed** | GitHub Actions local-regressions |
| Official GenLayer Direct Mode test suite (native SDK) | **4 passed** | GitHub Actions genlayer-direct |
| GenVM nondeterminism and consensus safety AST lint | PASS with documented SDK 0.3 entry-point recognition shim | GitHub Actions genvm-lint |
| GenVM SDK semantic validation | PASS | GitHub Actions genvm-lint |
| Studio/testnet real multi-validator deployment/finality | **NOT PERFORMED** | Requires GenLayer network + validators |

Successful verification workflow: https://github.com/maho0638/clausemirror-genlayer/actions/runs/41705418625

### What was tested

The native SDK tests exercise contract deployment, persistent storage initialization, owner authorization, creation and retrieval, real SDK nondeterminism interface with mocked LLM data, independent validator agreement/disagreement, immutable parent-linked revisions and invalid input handling. Mocked LLM responses are not actual model inference. The official linter semantically analyzes SDK 0.3 code; it does not execute a distributed network.

### Important fixes discovered during real CI

1. SDK 0.3 `gl.vm.run_nondet` was unsafe for validator-sandbox execution: changed to `gl.vm.run_nondet_default`.
2. SDK 0.3 persistent generic `TreeMap` requires `gl.storage.inmem_allocate` instead of direct constructor invocation.
3. The released `genvm-linter==0.11.1rc2` initially did not recognize SDK 0.3 safe nondeterminism entry. `scripts/compat_linter_sdk03.py` adds that API to its allowlisted safety entry patterns; it does not disable or ignore any lint rule. This patch should be removed when the upstream linter adds support.
4. Official `genlayer-test==0.30.0rc2` auto-parses LLM mocks; direct-mode test fixtures were adjusted to match SDK wire format.

### Explicit limitations

- **NOT a real GenLayer Studio/testnet transaction.** The leader/validator acceptance in Direct Mode is in-process, not a multi-node public consensus claim.
- **NOT a legal audit.** The result is a bounded AI judgment about user-supplied text, without external authenticity proof.
- Only the structured verdict is consensus-compared. `leader_note` is *not* validator-verified (`note_verified=false`).
- The full source text and receipt are publicly readable; do not publish confidential materials.
- No financial transactions, contract deployment or Portal submission were performed as part of verification.

Run the exact GitHub Actions configuration in `.github/workflows/python-tests.yml` for reproducible verification. View the run URL above for observed outcomes.