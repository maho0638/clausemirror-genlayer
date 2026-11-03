# ClauseMirror — verification register and release gate

Updated: 2026-11-04. This is **evidence tracking**, not an audit certificate.

## Current verified results

| Check | Status | Evidence / interpretation |
| --- | --- | --- |
| Python syntax | PASS | GitHub Actions `local-regressions` |
| Local deterministic security and control-flow tests | **65 passed** | GitHub Actions, test stub only |
| Official GenLayer SDK Direct Mode | **4 passed** | Actual SDK ABI/storage/permission/validator-callback handling; mocked LLM |
| GenVM static/safety lint | PASS | `genvm-lint lint`, RC 0.11.1rc2, narrow SDK 0.3 entry-name compatibility patch |
| GenVM SDK semantic validation | PASS | `genvm-lint validate`; no contract execution |
| GLSim RPC integration smoke tests | PENDING CI | Executes simulator RPC, not WASM GenVM or real consensus |
| Real GenVM runtime deployment | **NOT PERFORMED** | Requires local Studio / Docker |
| Studio multi-validator votes and finality | **NOT PERFORMED** | Requires Studio transactions with validators |
| Provider-diverse real LLM tests | **NOT PERFORMED** | Needs configured provider access |
| Live testnet deployment / on-chain gas measurement | **NOT PERFORMED** | Needs explicit user authorization before any transaction |
| Independent third-party security or legal audit | **NOT PERFORMED** | Consensus is no proof of legal accuracy |

CI evidence for the 65/4/lint results: [GitHub Actions #41705418625](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41705418625).

## Known defects resolved

1. Migrated to SDK 0.3 `gl.vm.run_nondet_default` for sandboxed verifier execution (not unsafe `run_nondet`).
2. Replaced unsupported generic `TreeMap()` instantiation with `gl.storage.inmem_allocate`.
3. Upgraded/pinned official GenLayer testing and linter RC tools after an old 404 GenVM artifact download failure.
4. Corrected the official Direct Mode fixture's double-JSON-decoding mismatch **in tests only**, without altering production LLM handling.
5. Hardened exact verdict/schema checking, illegal control/Unicode handling, authorization, immutable revisions, and version-linked receipts.

## Security and validity boundaries

- Every submitted clause and note is publicly visible on-chain; never upload confidential or personal data.
- The validators compare the three-valued verdict; the human-readable `leader_note` is *not* independently verified (`note_verified = false`).
- Different validators can agree and still make the same legal interpretation mistake. The supplied clauses are not authenticated against an external authoritative contract.
- Non-deterministic prompts and malformed model responses are fail-closed, but real provider/model behavior, runtime gas/fees, finality, appeals, and GenVM restrictions have not been exercised in Studio.
- The linter compatibility script only registers the SDK 0.3 safe nondeterministic API name in an older RC linter and does not switch off any checker. Remove it when upstream supports the name.

## Final release gate (needs actual evidence, not assumptions)

1. Run a disposable local GenLayer Studio (`genlayer up`) with at least **3 validators**, not `--leader-only`.
2. Deploy this exact commit/contract with a **test** account on localnet only; record code SHA, runner, Studio version, transaction ID and address.
3. Test accepted EN/TR `MATERIAL_DIFFERENCE`, `EQUIVALENT` and `INCONCLUSIVE` verdicts using controlled, clearly fictional public passages and different model/provider configurations.
4. Test owner-only `review` and `revise_target`, re-review rejection, immutable parent receipt, child link and JSON persistence.
5. Force validator disagreement and malformed AI JSON; verify a negative vote, transaction failure/rollback and unchanged `PENDING` record.
6. Confirm transaction **execution status**, consensus votes and finality, not just an RPC result.
7. Measure fee/gas and input bounds. Retain trace/logs and update this verification register with proof.
8. **Do not** merge to production, deploy to a public network, spend funds or submit to the GenLayer Portal without separate user approval.

Official references:
- https://docs.genlayer.com/developers/intelligent-contracts/testing
- https://docs.genlayer.com/developers/intelligent-contracts/tooling-setup
- https://docs.genlayer.com/developers/intelligent-contracts/tools/genlayer-studio
