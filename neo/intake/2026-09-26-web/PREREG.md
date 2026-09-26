# Pre-registration: 2026-09-26 web intake

Committed **before** any intake below was run through `neo/harness/gate.py`.

## Why these are admissible

The regime (LEDGER, 2026-09-26) admits only new primary material. Digesting the uploaded
Wayback archive (545 captures, `neo/materials/wayback/`) turned up three gsmg.io sources whose
text has never entered the ledger, the corpus or any campaign:

1. **Phase-2 page comment**, added between 2022-12-23 and 2026-04-05, right after `<body>`.
2. **SPA `/puzzle` card headline**, in every app.js bundle from 2020-06 to 2026-04.
3. **Finale page at `/`**, 2026-08-19. Tick 11 examined this page and called it "no puzzle
   content", so none of its text was ever tried. **Provenance caveat:** gsmg.io was parked and
   listed for sale from 2026-07-07 to at least 2026-08-10, so authorship of anything served
   after the lapse is unverified.

## Selection rule, fixed in advance

Take every solver-facing text unit in those three sources, **whole and verbatim**, one
candidate per intake. Excluded, with reasons:

- the finale's `legacy` section: the former trading-bot homepage copy, reproduced for the
  shatter animation;
- the link label "Follow the white rabbit": already in the corpus;
- the 14×14 grid: it is exactly the phase-1 grid, so it's spent;
- the timing constants (`1441`, `2442`, `3400`, `13950` ms): these are numbers in code, not
  text, and are not promoted to operands;
- every substring, case/spacing/punctuation variant and concatenation.

| intake | source | candidate |
|---|---|---|
| 01 | phase-2 page 2026-04-05 | `You made it to the next step! Good luck little bunny hunter ;)` |
| 02 | SPA app.js 2020-06-18 | `GSMG MEGANIGMA \|\| 5 BTC` |
| 03 | finale | `The lights are off.` |
| 04 | finale | `Nine years of chaos ended. One mystery remains.` |
| 05 | finale | `2017 — 2026` (U+2014) |
| 06 | finale terminal | `WARNING: carrier anomaly` |
| 07 | finale terminal | `Trace program: running` |
| 08 | finale | `SYSTEM FAILURE` |
| 09 | finale rain glyphs | `01010101010101010101010101010101010101010101010101010101GSMG.IO5BTCPUZZLECHALLENGE` |

## Protocol

The frozen gate, unchanged: {raw, sha256hex} × EVP-{MD5, SHA256} aes-256-cbc × {miniA, miniAB,
P32T, Cosmic}, which is 16 decrypts per intake and 144 in total. Also sha256(candidate) →
uncompressed P2PKH compared against the prize address. The gate may refuse an intake as spent;
a refusal is recorded as a refusal, not rerouted.

## Stop rule

If all nine come back null, the 2026 web material is closed. No variants, no concatenations,
no numeric constants and no second pass. Run from `neo/harness`:
`python3 gate.py ../intake/2026-09-26-web/NN_*.json`.
