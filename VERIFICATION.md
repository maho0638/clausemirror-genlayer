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
| GLSim RPC integration smoke tests | **2 passed** | [Actions #41760433361](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41760433361); simulator RPC, **not** WASM GenVM consensus |
| Real GenVM runtime deployment | **ATTEMPTED — NO SUCCESSFUL RECEIPT** | [Studio #41759025576](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41759025576) reached real local RPC and sent two deploy transactions; EVM reverted at gas ceiling, so neither transaction was decided |
| Studio multi-validator votes and finality | **NOT VERIFIED** | Real local RPC confirmed **5 mocked validator records** and consensus worker running; no completed contract vote/finality or rollback receipt yet |
| Provider-diverse real LLM tests | **NOT PERFORMED** | Needs configured provider access |
| Live testnet deployment / on-chain gas measurement | **NOT PERFORMED** | Needs explicit user authorization before any transaction |
| Independent third-party security or legal audit | **NOT PERFORMED** | Consensus is no proof of legal accuracy |

Latest complete CI evidence for 65 local / 4 SDK Direct / 2 GLSim / lint and semantic checks: [GitHub Actions #41760433361](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41760433361).

## Known defects resolved

1. Migrated to SDK 0.3 `gl.vm.run_nondet_default` for sandboxed verifier execution (not unsafe `run_nondet`).
2. Replaced unsupported generic `TreeMap()` instantiation with `gl.storage.inmem_allocate`.
3. Upgraded/pinned official GenLayer testing and linter RC tools after an old 404 GenVM artifact download failure.
4. Corrected the official Direct Mode fixture's double-JSON-decoding mismatch **in tests only**, without altering production LLM handling.
5. Hardened exact verdict/schema checking, illegal control/Unicode handling, authorization, immutable revisions, and version-linked receipts.
6. Added a disposable GitHub Actions Docker Studio gate: correct `eth_chainId=0xeec7` (61127), PostgreSQL migration compatibility, Redis, consensus worker, complete GenVM web config, and **five explicit local mock validators**. This is not equivalent to a passing contract-consensus test.
7. Diagnosed upstream Studio v0.121.25 `eth_estimateGas` hardcoding 500,000, causing `ConsensusMain#addTransaction` deployment reverts (499,997/500,000 gas); the integration-only localnet test uses a guarded 5,000,000 EVM gas floor. The mitigation is **not yet validated by a passing transaction**.

## Real Studio evidence log (2026-11-04)

- [Studio #41755434428](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41755434428): legacy CLI incorrectly returned chain ID `61999` instead of localnet `61127`. Zero validators.
- [Studio #41757597918](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41757597918): localnet chain ID corrected; consensus worker dependency blocked until Docker RPC health became healthy.
- [Studio #41758163544](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41758163544): consensus worker started; random-validator creation rejected with `No providers available` (no external model keys).
- [Studio #41759025576](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41759025576): confirmed five mock validators via `sim_countValidators`; both real Studio contract deployment attempts reverted at **500k EVM gas**. Test results **0/2 passed**; no GenVM consensus receipts.
- [Studio #41760433535](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41760433535): last checked **IN PROGRESS** with strict chain ID and five-validator gates already passed. Tests use strictly localnet gas override and corrected mocked `response` schema. **No success claimed until complete logs prove it.**
- The old CLI 0.39.1 and newer Studio/worker Docker versions are mixed in CI, with `latest` images for two services; this reproducibility risk remains until known-good image digests are pinned.

## Security and validity boundaries

- Every submitted clause and note is publicly visible on-chain; never upload confidential or personal data.
- The validators compare the three-valued verdict; the human-readable `leader_note` is *not* independently verified (`note_verified = false`).
- Different validators can agree and still make the same legal interpretation mistake. The supplied clauses are not authenticated against an external authoritative contract.
- Non-deterministic prompts and malformed model responses are fail-closed, but real provider/model behavior, runtime gas/fees, finality, appeals, and GenVM restrictions have not been exercised in Studio.
- The linter compatibility script only registers the SDK 0.3 safe nondeterministic API name in an older RC linter and does not switch off any checker. Remove it when upstream supports the name.

## Final release gate (needs actual evidence, not assumptions)

1. Run a disposable local GenLayer Studio (`genlayer up`) with **5 validator records** and working consensus worker, not `--leader-only`.
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
