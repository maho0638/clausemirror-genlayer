# ClauseMirror — Technical audit and test record

**Date:** 2026-11-03  
**Code:** `contracts/ClauseMirror.py` on `maho0638/clausemirror-genlayer`  
**Scope:** GenLayer SDK 0.3 contract semantics, state safety and authorization, independent verdict comparison, user-input boundaries, version history and native SDK test execution.

## Result

The current contract passes 65 deterministic control-flow and adversarial-input tests, 4 official GenLayer Direct Mode SDK tests, GenVM safety AST lint (using the documented SDK 0.3 API recognition shim), and GenVM SDK semantic validation. See the linked GitHub Actions workflow:
https://github.com/maho0638/clausemirror-genlayer/actions/runs/41705418625

## Defects found and fixed

- Earlier code used `gl.vm.run_nondet`, which SDK 0.3 treats as unsafe for validator execution. Replaced with sandboxed `gl.vm.run_nondet_default` and added an AST regression guard.
- Earlier `TreeMap()` generic constructors failed at actual SDK deployment. Replaced with `gl.storage.inmem_allocate(gl.storage.TreeMap[u32, T])` and proved via native SDK tests.
- An older GenVM test framework version fetched a missing GenVM runtime archive (HTTP 404). Pinned supported `genlayer-test==0.30.0rc2` and `genvm-linter==0.11.1rc2` for CI.
- The released linter's safety-entry registry lagged behind SDK 0.3. Added a narrow compatibility script that recognizes the new safe API without suppressing checks.
- Corrected Direct Mode mocked LLM JSON transport, and added native agreement/disagreement, immutable revision and permissions tests.
- Strict structured model output (`response_format="json"`), exact allowed verdict set, bounded notes, Unicode bidi/control/surrogate rejection and immutable revision lineage are tested.

## Residual risks / boundaries

This is **not** a formal security audit, full GenVM testnet deployment or independent network consensus/finality proof. Direct Mode uses mocked LLM responses; a Studio multi-validator environment can expose configuration, transaction-finality or real LLM behavior issues beyond these tests. Legal equivalence can remain wrong even if validators agree. Public on-chain clauses are not private, and source authenticity is not established. Never market it as legal advice or send sensitive contracts to the chain.

The receipt's `leader_note` is expressly not checked for semantic equivalence across validators; `note_verified=false` documents this. Only the `verdict` is independently re-evaluated.

## Relevant sources

- https://sdk.genlayer.com/main/_static/ai/api.txt
- https://docs.genlayer.com/developers/intelligent-contracts/equivalence-principle
- https://github.com/genlayerlabs/genlayer-testing-suite
- https://github.com/genlayerlabs/genvm-linter