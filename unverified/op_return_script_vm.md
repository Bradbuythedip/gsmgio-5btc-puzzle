# OP_RETURN as a puzzle-level virtual machine

**Status: closed. The load-bearing observation is a forced artifact, not a near-miss.**

## The hypothesis

The GSMG OP_RETURN outputs have the form `6a 47 <71 bytes>` (`OP_RETURN`, `PUSH71`,
payload). The proposal: conceptually "exit through the OP_RETURN door" and resume after it,
leaving `47 <71 bytes>` — a valid `PUSH71` that places the record on the stack. Then recurse:
the payload itself begins with ASCII `G` = `0x47`, so it too looks like `PUSH71`. At that
second level only **70** bytes remain, so it is *exactly one byte short* — and there happens
to be a byte sitting just outside the script (the first byte of the following output amount).
This was offered as the most specific piece of the hypothesis and the thing to test first.

It also leans on the Architect line *"return to the source codes, allowing a temporary
dissemination of the code you hopefully carry"* as a description of `OP_RETURN` then `PUSH71`.

## Why the one-byte shortfall is not evidence

For a payload of length `L` whose first byte is `B`, read as a push opcode: consuming `B`
leaves `L-1` bytes, while the push wants `B`. The shortfall is `B - (L-1)`.

Here `L = 71` and `B = 0x47 = ord('G') = 71`. So `L == B`, and:

```
shortfall = B - (L-1) = L - L + 1 = 1      always
```

| L | B | wants | has | shortfall |
|---|---|---|---|---|
| 71 | 0x47 `G` | 71 | 70 | **+1** |
| 71 | 0x48 `H` | 72 | 70 | +2 |
| 71 | 0x53 `S` | 83 | 70 | +13 |
| 60 | 0x47 `G` | 71 | 59 | +12 |

**Whenever the payload length equals its first byte's value, the shortfall is identically
+1 — by construction, for every such record, and it can never balance.** The entire
"coincidence" is that a 71-byte record begins with `G`, and `ord('G')` is 71. That is one
numerical coincidence in the record's *label*, not a structural near-miss pointing at a
hidden carry rule. JH and BH do not supply two independent instances of it either: they are
the same record format at the same length, so it is one coincidence observed twice.

## The proposed carry bytes are inconsistent

The "natural byte sitting immediately outside" is `0x0d` for JH and `0x4c` for BH — different
values, each the first byte of the following output amount and therefore arbitrary. A genuine
carry rule would yield the same structural byte in both cases. Two different arbitrary bytes
chosen to make two different records balance is fitting, not a rule.

It also requires crossing the script-length boundary, which Bitcoin's own encoding forbids —
so the rule cannot be inherited from Script semantics and would have to be asserted purely to
rescue the arithmetic.

## The other "opcodes" are ASCII artifacts

`isolveditwithanabacus` begins `0x69` and `secondanswer` begins `0x73`, cited as `OP_VERIFY`
and `OP_IFDUP`. But `0x69` is ASCII `i` and `0x73` is ASCII `s` — simply the first letters of
those words. Any English text read as script yields "opcodes"; that they are invalid ones
that fail immediately is the expected outcome, not a signal.

## What is correct in the hypothesis

The Bitcoin facts are right and worth preserving: Script has no loops and no `EVAL`; in
v0.1 `OP_RETURN` set `pc = pend`, and modern Bitcoin returns `SCRIPT_ERR_OP_RETURN`
immediately. There is no mechanism by which an OP_RETURN payload self-executes. The write-up
states this plainly and disclaims any exploit, which is correct and worth repeating: nothing
here is a Bitcoin vulnerability, and the proposed emulator was explicitly offline.

## Provenance caveat

The authenticated primary archive **deliberately excludes** these records: its README lists
"OP_RETURN dust" under *"Excluded on purpose"*, alongside other solver-derived constructions.
So the payload bytes above are not authenticated primary material, and this analysis takes
their claimed length and first byte as given rather than verifying them.

## Result

Closed on logic rather than on data: the off-by-one is forced whenever length equals first
byte, so it can never resolve, and the carry bytes that would resolve it are inconsistent and
unmotivated. No emulator needed. If someone wants to reopen this, the thing to establish
first is provenance of the records as primary material, and then a carry rule that is stated
in advance and yields the *same* structural byte across every record.
