# ClauseMirror — Bilingual Clause Meaning Consensus

**Live-verified GenLayer Intelligent Contract, public Studionet.**

ClauseMirror compares two *user-supplied public clauses* in different languages. It records **SAME**, **DIFFERENT**, or **UNCLEAR** only when GenLayer validators re-evaluate and accept the same bounded verdict.

## Contract API

Source: `contracts/ClauseMirror.py` (runner aligned with accepted Sightline project).

- `submit(case_id, source_language, target_language, source_clause, target_clause)` — create a unique public case, attributed to submitter.
- `review(case_id)` — requester-only; independently re-execute AI comparison under GenLayer validator consensus, once.
- `get_case(case_id)` — read stored JSON, preserving the original input clauses and controlled verdict.

Each public case ID is caller-generated and must be unique. Valid language tags are ASCII letters (2–12 chars). Input clauses are limited to 1,200 characters. Invisible Unicode controls are blocked. There are no transfers, escrow or administrative exceptions.

**Limitations:** A validator-approved AI verdict is not legal advice, a factual authenticity certificate or an endorsement of the supplied clauses. Everything submitted is public blockchain data: do not publish confidential or personal information.

## Verified live Studionet execution

- Contract: `0x2c3DFCAF3588b15c3be25Bda056C7bB4e6406B86`
- [GenLayer Explorer](https://explorer-studio.genlayer.com/address/0x2c3DFCAF3588b15c3be25Bda056C7bB4e6406B86)
- Submitted pair: `0xdaab6e261fc7eb2d2ab8b3570d94bfdb546585abab51aaa5c321c12760ae1a9c`
- Reviewed pair: `0x8244c8493ff883420a0918dd369cb75f79fb1b95e398e7b8ac5784313b5e1331`
- Read-back: `DIFFERENT` for 14-day vs 7-day cancellation example
- [Successful end-to-end network run](https://github.com/maho0638/clausemirror-genlayer/actions/runs/41828772045)
- Local Direct Mode and GenVM lint: `.github/workflows/checks.yml`; hosted network proof: `.github/workflows/studionet.yml`

The testnet uses development accounts. No mainnet transaction is claimed.

## Portal submission

See [SUBMISSION.md](SUBMISSION.md) for the ready-to-paste title, concise English description and required repository + explorer evidence.
