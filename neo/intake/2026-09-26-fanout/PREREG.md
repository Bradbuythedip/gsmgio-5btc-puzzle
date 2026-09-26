# Pre-registration: the 3GSMG24T fan-out and the 37mh… funder (2026-09-26), before the live run

Fixed by the user and recorded before the single live pass of `harness/receipt_lookups.py` (tick 92 tooling plus the
review fixes). Topology only: no address, key, amount, txid or script becomes an AES candidate, whatever the outcome.

## H1 — the treasury / fuel model (12 → 12)

The 15,000 sat that `37mh7EYetVKAesxqzv968sTYqSLF8dE6oD` (P2SH-P2WSH 2-of-2) paid to 3GSMG24T in `1f8eb99e…` was cut, by
3GSMG24T's own self-splits, into exactly **12 spendable outputs**. These are consumed one-for-one by the **12 known 2020
emissions**:

| emissions | recipients | outputs consumed |
|---|---|---|
| 6 checkpoint memos | `1Jqq37…` `1GyT5W…` `18Cchr…` `1K23RS…` `1AD2wf…` `1M5ypv…` | 6 |
| 1 bare payment | `1NULY7…` (1,050 sat) | 1 |
| 2 "Good job, Neo!" | `148XH2…` `13HGhj…` | 2 |
| "Halving" | the prize, 700 sat | 3 |

**PASS** iff the tree rooted at `1f8eb99e…`'s 3GSMG24T output has exactly 12 non-split leaf-spends, and those are exactly
these 10 transactions consuming exactly those 12 outputs: no fuel output unspent, none spent elsewhere, no other recipient.
Anything else is a **FAIL**, reported with the difference. PASS promotes the treasury model: the creator funded the wallet
and pre-cut message fuel ahead of time.

## H2 — the 2021 refill

`a82052a2…` pays out 4 × 5,000 sat, more than the 2020 fuel. Identify the inbound funding it spends and record its signer.

## Promotion of `37mh…` as creator infrastructure

PROMOTE only if at least one holds:
- **(i)** its ancestry reaches a creator-trail signer (`1EtbTv…`, the prize key, `1GSMG1CLx…`, `17ucy1…`);
- **(ii)** one of its public keys matches authenticated GSMG material;
- **(iii)** its full history is narrowly GSMG-specific: ≤ 10 transactions, ≥ 50% touching a GSMG-labelled address;
- **(iv)** it also funds later creator activity: it signs two or more separate inbound fundings of 3GSMG24T that 3GSMG24T
  then spends, for example the 2021 refill.

Otherwise, and in particular when its history is broad and unrelated: operational wallet infrastructure; close.

H1 and the promotion are judged separately. A 12 → 12 PASS does not by itself promote `37mh…`, and a FAIL does not by
itself close it.
