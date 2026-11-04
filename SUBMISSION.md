# GenLayer Portal contribution — ClauseMirror

**Category:** Developer → Intelligent Contracts
**Title:** ClauseMirror — Bilingual Clause Meaning Consensus

## Notes / Description (below 1,000 characters)

ClauseMirror is a deployed GenLayer Intelligent Contract for comparing the operative meaning of two public clauses in different languages. A requester records both clauses and requests a one-time AI review. GenLayer validators independently assess the same evidence and must agree on the controlled verdict SAME, DIFFERENT, or UNCLEAR before the result is stored. Duplicate IDs, unauthorized review, repeated reviews, malformed AI responses, and unsafe Unicode are rejected. The original texts remain queryable. Unlike a translation demo, this primitive creates durable review receipts and verifies a decisive semantic outcome through real consensus. On Studionet, deployment, submission, review and read-back succeeded; the 14-day versus 7-day cancellation example returned DIFFERENT. It is not legal advice or document-authenticity proof.

## Required evidence (enter as separate URLs)

**GitHub Repository**
https://github.com/maho0638/clausemirror-genlayer

**GenLayer Explorer Contract**
https://explorer-studio.genlayer.com/address/0x2c3DFCAF3588b15c3be25Bda056C7bB4e6406B86

## Additional evidence

- Live network CI: https://github.com/maho0638/clausemirror-genlayer/actions/runs/41828772045
- Live source code: https://github.com/maho0638/clausemirror-genlayer/blob/fix/studionet-compatible-20261104/contracts/ClauseMirror.py
- Submission tx: https://explorer-studio.genlayer.com/tx/0xdaab6e261fc7eb2d2ab8b3570d94bfdb546585abab51aaa5c321c12760ae1a9c
- Review tx: https://explorer-studio.genlayer.com/tx/0x8244c8493ff883420a0918dd369cb75f79fb1b95e398e7b8ac5784313b5e1331

## Limits

Live proof is on public **Studionet**, not Bradbury or mainnet. Independent validator execution does not prove semantic correctness. Never submit private legal data. No Portal submission was made automatically.
