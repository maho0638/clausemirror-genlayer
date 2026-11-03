# ClauseMirror source review — 3 November 2026

## Scope

A code-level review of `contracts/ClauseMirror.py`, unit tests, and GitHub CI workflow. It is **not** a security audit or a successful GenVM execution report.

## Fixes applied after initial prototype

1. The official current `gl.nondet.exec_prompt(..., response_format="json")` path replaced brittle raw text `json.loads` handling. Unexpected result types, extra keys, empty/oversized notes, or invalid decisions fail closed.
2. The validator path validates the leader's structured return, independently evaluates the exact original evidence, votes `False` on malformed independent output, and compares only the decision-bearing verdict. The leader note is explicitly unverified.
3. Input and model notes now reject dangerous Unicode controls, unpaired surrogate code points and bidirectional overrides. Validation occurs before trimming so trailing invisible characters cannot escape checking.
4. Added tests for forged leader output, malformed validator output, invalid Unicode, native Turkish and Arabic text, revision preservation, and repeated-case state invariants.
5. A GitHub Actions workflow will run `genvm-lint check` once code is committed and GitHub Actions runs.

## Tests performed and observed results

| Verification | Result |
|---|---|
| `python -m compileall -q contracts tests` | PASS, Python 3.13.5 |
| `python -m pytest tests/ -q` | **57 passed**; mocked GenLayer runtime |
| Python AST review of imports, public methods, storage definitions and nondet call placement | PASS manual structural review |
| GitHub workflow YAML parse | PASS |
| `genvm-lint check contracts/ClauseMirror.py` | **BLOCKED**: no official package, no PyPI DNS |
| `genlayer-test` direct-VM suite | **BLOCKED**: no package, no PyPI DNS |
| Full GenVM/Studio multi-validator deployment & transactions | **NOT RUN**: no Studio/CLI/Docker or network access |
| Formal methods, live-network gas & appeals | **NOT RUN** |

## The remaining critical release gate

The contract must pass **official linter and real GenLayer Studio/GenVM multi-validator tests** before being declared deployed or production-ready. A 57/57 stubbed test result does not imply 100% correctness, and even real validator consensus cannot prove that a translation's legal interpretation is objectively true.

## Source references

- https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms
- https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism
- https://docs.genlayer.com/developers/intelligent-contracts/features/storage
- https://docs.genlayer.com/api-references/genlayer-linter
- https://docs.genlayer.com/developers/intelligent-contracts/testing

## SDK v0.3 compatibility upgrade

3 November 2026: The project was adapted to the SDK 0.3 import/API changes using the official SDK API changelog: `import genlayer as gl`, `gl.contract.Contract`, `gl.storage.TreeMap`, plain integer initializers for `u32` storage, and `gl.vm.run_nondet` (the replacement for `run_nondet_unsafe`). The source was checked against the current SDK reference; official linter and Direct Mode execution were delegated to repository CI, and full Studio multi-validator testing remains separate and cannot be asserted without a transaction receipt.