# Pre-registration: affine-nonce trapdoor test (2026-09-26), before the run

User-directed. Tests whether the GSMG creator planted an algebraically weak nonce in the prize
key's own 2020 halving signatures (materials/chain/tx_halving_spend.hex, verified tick 70). Uses
only the creator's public on-chain signatures; no discrete-log search, no AES, no candidate soup.

Fixed accept predicate (cannot be tuned): a recovered scalar d counts only if d*G hashes to the
prize address 1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe. For a normally-generated nonce no (a,b) yields
such a d; a hit means a relation was deliberately built in.

Fixed, small instruction set (a,b) for k = a*d + b, from "neighbors, half and double":
  k in {d, d+1, d-1, 2d, d/2, -d, -d+1, -d-1, 2d+1, 2d-1, d/2+1, d/2-1}.
Single-signature: d = (z - s*b)/(s*a - r) mod n, require d*G == Q.
Pairwise nonces (k_j = a*k_i + b): solve the resulting linear equation in d, require d*G == Q.
Repeated nonce (equal r across inputs): classic recovery, require d*G == Q.
Point identity: lift each r to both parities and to x=r+n<p; compare R against
  +/-Q, +/-(Q+G), +/-(Q-G), +/-2Q, +/-(Q/2).

The "Robert Doty -> R.y" comparison has no operand: the authenticated OP_RETURN payloads on the
trail are ASCII text ("Halving", "GSMG.io neighbors, half and double"), not 32-byte binary fields.
Not run.

Decision: HIT if any branch yields d with d*G == Q (report and stop). Otherwise the affine-nonce
branch is closed with a clean negative; no widening of (a,b), no other signatures (840003 has no
raw hex; the segwit OP_RETURN txs cannot be checked offline).
