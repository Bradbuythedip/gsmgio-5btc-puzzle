# Pre-registration: the 196 = 91 + 14 + 91 scalar test (2026-09-26), committed before the run

User-relayed script, run as specified. Its ambiguous parts are fixed here before any scalar is computed.

**Predicate (only this):** compressed and uncompressed P2PKH of each scalar compared with the prize
`1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` and `17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa`. No AES: the script
defines no decrypt, and gate.py would refuse these strings as corpus-spent.

**Objects.** DBBI = soup[:91] (a–i), VIC = the 91-letter certified sentence, both as ASCII.
The "14-bit middle" has two fixed definitions:
- `M_diag`: the main diagonal of the authenticated grid, (0,0)→(13,13) = `01000000111111`. This is the
  14 in 196 = 91 + 14 + 91 (upper triangle / diagonal / lower triangle).
- `M_spiral`: bits [91:105] of the authenticated CCW spiral (URL bits 91–104).
The draft's "rows 7–8" is 28 cells, not 14, so it is not run. Both middles are functions of the
known URL (tick 69), so no key can hide in them.

**Scalars:** sha256(x) mod n unless stated.
1. sha256(DBBI), sha256(VIC). The latter was already run at campaigns 34 and 43; it is re-checked here.
2. Residual, two renderings. `R_auth` = (DBBI a=1..9 − VIC A=1..26) mod 26 rendered A=0, the
   authenticated YOUWON stream. `R_literal` = the draft's literal `(ord(d) − ord(v)) % 26 + 65`. It
   mixes lower- and upper-case ASCII offsets, so it equals `R_auth` shifted by 6 (YOUWON → EUACUT).
3. sha256(DBBI ‖ M ‖ VIC), with M as 14 ASCII '0'/'1' characters (196 symbols), for both middles.
4. M as a scalar, two readings for both middles: int(M, 2) (the 14-bit value), and
   int.from_bytes(M as ASCII) (the draft's literal behaviour when MIDDLE_BITS holds the ASCII bits).

**Decision:** any match is a HIT: report and stop. Otherwise the 196-split correspondence is closed as
"thematic, not cryptographic" (the draft's own rule). No reorderings (VIC ‖ M ‖ DBBI), no other
middles, renderings, hashes or maps.
