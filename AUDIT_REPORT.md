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
| `python -m pytest tests/ -q` | **57 passed at the initial GitHub run**; mocked GenLayer runtime (subsequent local suite: 65 passed) |
| Python AST review of imports, public methods, storage definitions and nondet call placement | PASS manual structural review |
| GitHub workflow YAML parse | PASS |
| `genvm-lint check contracts/ClauseMirror.py` | **BLOCKED**: no official package, no PyPI DNS |
| `genlayer-test` direct-VM suite | **BLOCKED**: no package, no PyPI DNS |
| Full GenVM/Studio multi-validator deployment & transactions | **NOT RUN**: no Studio/CLI/Docker or network access |
| Formal methods, live-network gas & appeals | **NOT RUN** |

## The remaining critical release gate

The contract must pass **official linter and real GenLayer Studio/GenVM multi-validator tests** before being declared deployed or production-ready. A passing stubbed test result does not imply 100% correctness, and even real validator consensus cannot prove that a translation's legal interpretation is objectively true.

## Source references

- https://docs.genlayer.com/developers/intelligent-contracts/features/calling-llms
- https://docs.genlayer.com/developers/intelligent-contracts/features/non-determinism
- https://docs.genlayer.com/developers/intelligent-contracts/features/storage
- https://docs.genlayer.com/api-references/genlayer-linter
- https://docs.genlayer.com/developers/intelligent-contracts/testing

## SDK v0.3 compatibility upgrade

3 November 2026: The project was adapted to the SDK 0.3 import/API changes using the official SDK API changelog: `import genlayer as gl`, `gl.contract.Contract`, `gl.storage.TreeMap`, plain integer initializers for `u32` storage, and a prior **incorrect** use of `gl.vm.run_nondet` (unsafe in SDK 0.3), subsequently corrected to `gl.vm.run_nondet_default`. The source was checked against the current SDK reference; official linter and Direct Mode execution were delegated to repository CI, and full Studio multi-validator testing remains separate and cannot be asserted without a transaction receipt.

## Observed official CI failure / remediation

- `https://github.com/maho0638/clausemirror-genlayer/actions/runs/41684508789`: 57 local checks and Python compilation passed on GitHub's Python 3.12 runner.
- `genlayer-test` stable 0.29.2 failed during SDK artifact setup with `urllib.error.HTTPError: HTTP Error 404: Not Found` while downloading `v0.3.0-rc7/genvm-universal.tar.xz` before attempting to load ClauseMirror.
- Linter was skipped in the original order. CI was revised to use the officially published September RC packages (`genvm-linter==0.11.1rc2`, `genlayer-test==0.30.0rc2`) and to run lint first. Passing results must be verified from a new workflow run.
- No Studio consensus run or testnet finalization has occurred.

## 3 November 2026 — critical SDK 0.3 consensus correction

The original code called `gl.vm.run_nondet(produce, verify)`. The official GenLayer SDK 0.3 specification explicitly redefines `run_nondet` as **unsafe**, with no validator sandbox, and introduces `run_nondet_default` for the previous safe behavior. This was a genuine technical bug masked by a fake runtime that incorrectly modeled the old API. It is now corrected to `gl.vm.run_nondet_default(produce, verify)` and the test stub deliberately rejects any future use of the unsafe entry point. Additional tests check forbidden Unicode format controls and SDK 0.3 symbols. **65 deterministic/local tests pass.**

CI is split into independent jobs for local regressions, AST+semantic linter, and genuine GenLayer Direct Mode. **Neither official linter nor direct/Studio tests are yet reported as passing in this audit.** The 404 release-asset obstacle has not been demonstrated fixed. Never claim 100% GenVM compatibility or real consensus validation from local tests.