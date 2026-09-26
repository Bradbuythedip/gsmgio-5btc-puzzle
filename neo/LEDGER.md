# Neo continuous-mode ledger

Running log of verified ground truth, pinned conventions, campaigns run, and open
threads. Newest session at the bottom. Everything here is reproducible from
`neo/harness/` + `neo/materials/`.

---

## Session 2026-09-25 — endgame corpus assembled, convention pinned, campaigns started

### Verified ground truth (primary sources: this repo's notebooks/assets + page screenshot)

Four unsolved AES locks, all openssl `Salted__` unless noted:

| id | bytes | salt | source |
|---|---|---|---|
| miniA | 48 (ct 32) | `3ab585348552415d` | SalPhaseIon page tail, after "sha b4 first hint is your last command" |
| miniB | 48 raw, no header | — | SalPhaseIon page tail, after the abba-binary "enter" |
| miniAB | 96 (ct 80) | `3ab585348552415d` | A‖B joined ("enter" = newline between two lines of one blob) |
| inner96 | 96 (ct 80) | `b45a5e3d827593ca` | tail of phase-3.2 plaintext (phase3-assets/phase3.2.txt) |
| cosmic | 1344 (ct 1328) | `2d3f6fe06dc950e6` | "Cosmic Duality" section of SalPhaseIon page |

- SalPhaseIon page string (1075 letters, space-separated) copied from salphaseion.ipynb;
  byte-identical to the copy in the (otherwise junk) jackdevs66/GSMG5_CDuality repo.
- Cosmic Duality b64 (28×64 chars) taken from jackdevs66 repo; first ~13 lines verified
  visually against salphaseion-assets/SalPhaselonCosmicDuality.png. Residual risk: last
  lines unverified against an independent archive (gsmg.io and web.archive.org are
  egress-blocked here). TODO: verify via another archive/mirror.
- SalPhaseIon tail structure (z-separated):
  `…letters… z lastwordsbeforearchichoice z thispassword z
  shabefourfirsthintisyourlastcommand [miniA b64] z? enter-binary [miniB b64]
  shabef anstoo`
  Readings: "SHA b4 — first hint is your last command", "SHA b4 answers too".
- Still-undecoded letter blocks: `dbbib…` head (165 chars, alphabet a–i) and `faed…`
  block (~1000 chars, a–i). The decoded segments used a=1…i=9, o=0, digits→int→hex→ascii.
- Phase 3.2 fully solved upstream of the inner blob: EBCDIC cp1141 → Beaufort key
  `thematrixhasyou` → Architect speech containing: "seven intertwined passwords",
  "reinserting the prime basics", "over twentythree ciphers sixteen encryptions",
  "take the private key youve earned it", "worth hundred fourty of the investment".
  VIC (digits 1,4; alphabet `fubcdora/lethingkymvpszjqwx.`) →
  "IN CASE YOU MANAGE TO CRACK THIS THE PRIVATE KEYS BELONG TO HALF AND BETTER HALF
  AND THEY ALSO NEED FUNDS TO LIVE".
- 2023-02-23 official hint (binary→ascii): "yellow blue primes matrix sumlist last words
  before archichoice yinyang we wont give away thepassword its in front of your eyes but
  youre not seeing it very last step is a true give away promised" — seven components,
  matching "seven intertwined passwords".
- Phase-0 14×14 grid (materials/phase0_grid.txt), b=blue=1, y=yellow=0 proven by the
  phase-0 decode ("Yellow has a number and so does Blue" = 0 and 1).

### Pinned convention (empirical, 3 positive controls)

`openssl aes-256-cbc -a -d -pass pass:<sha256hex(password)>` with EVP_BytesToKey(SHA256)
decrypts phase2_aes (password `causality`), phase3_aes (phase-2.2 monster password),
phase3.2-aes (`jacquefresco…`). So the creator's habit: **passphrase = lowercase sha256
hex of the human answer** ("sha b4"). Harness self-test reproduces all three
(`aes_try.py self_test`). Note phase-3.2 plaintext is ~60% printable (EBCDIC section) —
acceptance rules must not assume fully-printable plaintext.

### Harness rules (false-positive control)

Accept = strict PKCS#7 AND (pad≥4 [~2⁻³² chance] OR ≥4-byte magic prefix OR head/whole
printable ≥0.85/0.90). pad∈{1,2,3} with garbage bytes is noise (observed: 3 chance
"hits" in 75k trials before tightening; the prior sessions' "cosmic_1327b_decrypted"
1-byte-pad artifact is exactly this failure mode — treat any such claim as false).

### Campaigns run (log: neo/attempts/*.jsonl)

- campaign_01: ~75k trials. Singles (labels, Matrix quotes, phase passwords, VIC/beaufort
  phrases, follow-the-white-rabbit readings) + bounded 7-token cartesian in hint order and
  SalPhaseIon order; each candidate also as sha256hex/SHA256HEX/sha256²/sha256d; against
  all 5 targets × 4 KDF variants. **No verified hit.**

### Prior-session archive

`neo/prior-sessions/2026-09-25-S1S4/` — S1–S4 scalar-construction ledger + scripts as
uploaded (that family is BLOCKED on unrecoverable S0 and stays parked; the "cosmic tree"
material it references is demoted solver-derived artifact).

### Open threads (next moves, ranked)

1. **Structural decode of `dbbib` (165) and `faed` (~1000) blocks** — sweep letter→digit
   /base-9/polybius/keyed mappings and score decodings for `U2Fsd`/`Salted__`/printable
   structure. A hit here is self-proving and likely reveals the real instructions.
2. **Matrixsumlist families** — phase-0 grid row/col sums, prime-indexed variants
   ("primes matrix sumlist" may bind: sums over prime rows/cols/cells), spiral-order
   variants (the phase-0 spiral is proven mechanics), letter-grid sums; each × format
   variants × sha-b4; test against all locks.
3. **Order/intertwine variants** of the 7 components (permutations, z-joins, interleaves).
4. **Verify cosmic blob tail** against an independent mirror.
5. Cosmic Duality image steganography angle (the yin-yang book cover) — untouched.

- campaign_02: ~28k trials. Letter blocks verbatim (head/faed/page ± spaces), column-major
  transpositions, all-divisor-width row/col sum lists (both digit maps, 3 formats),
  prime-position keeps/drops, block sums (head 422, faed 3079=prime, 3501). **No hit.**
- Decoder sweep on head/faed (digits→int→hex→ascii, base-9→bytes, letter-pair decimal/b81,
  mod-26): no printable/self-proving output. head=91 (7×13), faed=570 (19×30 etc.);
  head has no 'o' (no zero digit) → agda/cfob scheme structurally excluded for it.

### Roadmap for next iterations
1. mod-9 Beaufort/Vigenère on head/faed with puzzle-vocab keys, then agda/cfob decode.
2. 7-token order permutations (values fixed to best guesses), z/newline/space joins,
   CamelCase variants; word-number forms; "23 16 7" numbers from beaufort text.
3. Image forensics: hints/cosmic-duality-book.png + salphaseion-assets PNG (appended
   data, LSB, palette).
4. Import kaibuzz0 + remaining upstream issues as tried-lists/exclusions.
5. Independent verification of cosmic blob tail bytes.

- Mod-9 cipher sweep (Vigenère/Beaufort with 35 vocab keys, 8 Caesars, atbash) on
  head/faed, decoded via digits→int→hex→ascii: nothing scored. Logged as excluded.
- PNG forensics: repo copies of cosmic-duality-book.png / 2022-12-10-cosmic.png are
  2023 gnome-screenshot re-captures; SalPhaselonCosmicDuality.png and puzzle.png have
  clean IEND, no appended data. Stego on these *copies* is a dead end (originals live
  on gsmg.io / Telegram, both unreachable from this container).
- Book cover identified: Time-Life "Mysteries of the Unknown — Cosmic Duality".
- campaign_03 (~1.21M trials): URL-hash/"in front of your eyes" chain (89727c…, page
  caption string, all known passphrase sha256s), book vocab, 23/16/7/140 numbers,
  full 7! order permutations of the seven components (label set and value set),
  z/newline/space/dash joins. **No hit.**

Cumulative excluded trials this session: ~1.34M (see neo/attempts/*.jsonl for the
pad-valid subset; all candidates reproducible from campaign scripts).

### Loop tick 2 (2026-09-25)
- Harness: added miniB [iv||ct] layout target, raw-key mode (key=sha256 digest, -K style);
  self-test still green. 7 targets × 5 KDF modes.
- campaign_04: spiral ring sums, prime-indexed row/col/cell sums, URL byte popcounts,
  case variants (Title/UPPER, MatrixSumList spellings). No hit.
- Reran campaigns 01–03 over expanded targets/KDFs. No hit.
- campaign_05 (big bounded cartesian, pinned-convention-only s2 + {raw,sha256hex}):
  433k candidates — 7-component product with Dutch variants (geel/blauw/priemgetallen),
  long prime strings, 4-component SalPhaseIon-order product, and "sha b4 ans too"
  structures (concatenated per-answer sha256 hexes, 2- and 3-part). 3.46M trials. No hit.
- Sizes note: inner96/miniAB ct=80 fits exactly a 64-char hex privkey + LF (65→pad 80);
  miniA ct=32 fits ≤31 chars (an instruction/passphrase?). These stay the priority targets.
- Excluded: colored-cell spiral reading (restates URL — unverified/phase0_yellow_blue_counts.md).
  Page letter-grid has no intrinsic width (screenshot shows soft wrap): "the matrix" = phase-0 grid.

Next tick: harvest vocabulary from unread hint images (2020-08-02, 2021-01-21, 2021-12-02,
2021-12-25, 2023-01-09/12, 2023-08-*, 2024-*, 2026-07-12-other), add sha1-EVP mode, then
vocabulary-driven campaign 06.

### Loop tick 3 (2026-09-25)
**Live Telegram intel (user-supplied screenshot, "GSMG Puzzle Solvers", today):**
Two 32-byte `Salted__` blobs posted by a π-named account:
`U2FsdGVkX18yZW/gbclQ5kgE0hTuyBQYgDM+3Q6iBEw=` and
`U2FsdGVkX18yZW/gbclQ5vnkmWwR8NfqVPIKhUiGDu4=`
**Analysis: both are splices of the public Cosmic Duality blob** — ct(X) = cosmic ct
block 8 (byte offset 144), ct(Y) = cosmic ct block 18 (offset 304), salt =
`32656fe06dc950e6` (= cosmic salt with first two bytes changed 2d3f→3265, tail
identical). The accompanying claim "decrypts using sha256('GSMGIO....prBe') and raw
keys" does NOT verify: tested EVP md5/sha256/sha1 ×128/256 with passphrase = caption
and its sha256hex, raw-digest keys (-K style, iv=0), in-stream IVs (preceding cosmic
block), crafted-IV equality, whole-cosmic bulk decrypt under those keys — all random
(printable ≈0.37 baseline). Verdict: community splice/noise unless a future message
supplies a different key. TG "ETA 1 hour / Congratulations?" chatter has no
cryptographic backing in the screenshot.

**New creator-source vocabulary/ops from previously unread hint images:**
- 2021-12-25 official: "some characters need to be 'zeroed out'" (+ primes required)
- 2021-12-02: acrostic THERE IS ANOTHER DOOR
- 2021-03-01: prime part uses 2,3,5,7; "too many combinations" (selection/order matters);
  Jrk: "You are at the prime part already???" (prime part is late-stage)
- 2023-01-09: "At least prime number is very important to get any further"
- 2023-01-12: "theory of everything is also still a valid path to reaching the private key"
- 2023-08-03: "shine us some 'light'"; "Are you really looking for just the btc...?";
  "the hardest part is done"
- 2023-08-06: "The puzzle talks for me"; Mr Robot last-scene wish; "Once you hit a
  'ying yang', you'll be able to solve it the same day" (recognizable checkpoint!);
  "salvation part" (SalPhaseIon wordplay); creator located in France
- 2026-07-12: "The '5' btc was never the actual prize. That was only a tiny fraction."

- campaign_06 (~355k trials): new vocab, o→0 / drop-o "zeroed out" transforms over key
  tokens, URL yellow-position zeroing, all 2357 permutations/ordered subsets alone and
  in the seven-token frame; added sha1-EVP mode. **No hit.**

Next tick: read remaining unread images (2020-08-02, 2021-01-21, 2024-*, 2020-05-11,
2020-06-07, 2021-02-12/03-14/04-16/05-06), then consider Beaufort-key reuse
("thematrixhasyou") on the letter blocks under 26-letter interpretation, and
"connect the last pieces" composite orderings.

### Loop tick 4 (2026-09-25)
- Remaining hint images read: 2020-08-02 (second half maybe another puzzle "or not at all";
  nobody found the extra door), 2021-01-21 ("a few might not require the internet
  anymore" → final stage is fully offline once you have the materials), 2024-04-19
  (halving; prizes besides banter: "a private key, some 'obscure' intel"; "see you in
  4 years"), 2024-04-10 ("1357 blocks to go" — halving countdown, also odd-digits wink).
- campaign_07 (~19k trials): char-interleaved "intertwined" composites (labels, values,
  per-answer sha256s; pad+cut modes), pairwise intertwines (half/betterhalf, yin/yang…),
  mod-26 Vigenère/Beaufort decodes of head/faed under 8 puzzle keys used as passwords,
  reinsert-2357-at-primes into rowsums, halving numbers (840000/630000/dates), 1357
  permutations. **No hit.** Mod-26 decodes also scored for English: chance-level only.

Next tick: (a) "zeroed out" digit maps — for head/faed try a=1..i=9 with each letter
X∈{a..i} remapped to 0 (9 variants/block) → int→hex→ascii; (b) letter-as-separator
segmentations (9 variants/block; segment lengths as digits, segments as digit groups);
(c) column-wise Vigenère on head 7×13 keyed "matrixsumlist" per column.

### Loop tick 5 (2026-09-25)
- campaign_08 (~4k trials): zeroed-out digit maps (each of a–i as the 0, mirroring
  agda/cfob's o=0) on head/faed → int→hex→ascii: no printable break (best 0.53 = chance);
  letter-as-separator segment-length lists; "matrixsumlist"-keyed per-column shifts of
  the 7×13 head (mod 9/26, ± , row/col-major reads). **No hit.**
- campaign_09 (~9.0M trials): dwyl words_alpha (370,105 English words) + SecLists 10k
  common passwords, raw and sha256hex, s2, vs miniA/miniAB/inner96/cosmic; integers
  0–999,999 raw+sha vs miniA/miniAB/inner96. **No hit** (2 pad-2 near-misses = chance).
  → Under the pinned convention, miniA's password is NOT a single English word, common
  password, or number ≤ 999999. It is composite/derived, consistent with the puzzle's
  established style (long concatenations + sha256).
  Wordlists (scratchpad only, not committed): words_alpha.txt (dwyl/english-words),
  10k-most-common.txt (danielmiessler/SecLists).

Cumulative logged trials this session: ~14.7M.
Next tick: two-word combinations of puzzle-core vocabulary (bounded ~1-2M), miniA-focused;
and read upstream issues index for community tried-lists worth importing as exclusions.

### Loop tick 6 (2026-09-25)
- Independent corroboration (user-shared ChatGPT status) lands where this ledger already
  is: `thispassword`-as-literal CLOSED; `thispassword`-as-reference-in-SalPhaseIon OPEN;
  the final Phase-3.2 **96-byte envelope (inner96)** is the PRIMARY authenticated lock;
  S1–S4 ±2^38 BSGS blocked (needs S0). Confirms inner96 as the right target.
- Scope note: a "reverse-engineer the signature / time-lock" idea was raised. Deliberately
  NOT pursued — recovering a key from ECDSA signatures is a generic wallet-flaw technique
  (e.g. nonce reuse), not the creator's intended decode path, and not something to build
  as general tooling. A real time-lock (CLTV/CSV) would live in a spend script, not the
  AES envelope. Staying on the intended derive-the-key-from-puzzle-content track.
- campaign_10 (~125k trials): all ordered two-token combinations of a 55-word core
  vocabulary (labels, decoded answers, Matrix/Mr-Robot terms, VIC/beaufort phrases,
  creator lines) × 5 joiners × {raw, sha256hex}, s2, vs the four locks. **No hit.**

Next tick: three-token bounded combos on the highest-signal subset for inner96; and a
careful re-read of the SalPhaseIon `shabef...` grammar (the repeated "sha b4" framing)
as a construction recipe rather than treating decoded labels as passwords.

### Loop tick 7 (2026-09-25) — the circulating XOR theory, tested end to end

Added `neo/harness/btc_addr.py`: dependency-free secp256k1 → P2PKH, validated against
canonical known-answer vectors (privkey 1 and 2, compressed + uncompressed) so that a
negative result from it is trustworthy. `neo/harness/verify_xor_theory.py` runs the test.

**Claim A.1 — CONFIRMED (arithmetic reproduces).**
XOR of sha256 over the seven published tokens
(matrixsumlist, enter, lastwordsbeforearchichoice, thispassword, matrixsumlist,
yourlastcommand, secondanswer) does equal
`a795de117e472590e572dc193130c763e3fb555ee5db9d34494e156152e50735`. The number is real.

**Claim A.2 — FALSIFIED. This is the load-bearing failure.**
That value does NOT decrypt the Cosmic Duality blob. Tested as password (hex lower,
hex upper, recomputed) × EVP md5/sha256/sha1 × 128/256-bit, and as a raw 32-byte key
with zero IV, doubled-salt IV, and ct-prefix IV. No valid PKCS#7 + structure anywhere.
So the writeup's "known working shape: XOR(sha256(t1..t7)) → OpenSSL password → Cosmic
Duality blob" is **not** a working shape. The premise the whole XOR branch rests on is
unsupported.

**Claim B — FALSIFIED.** 121 bounded XOR candidates around the witness scalar
`abc09ead…` (XOR against the claimed key, the recomputed XOR, sha256 of each of the
seven tokens, yinyang, yellowblueprimes, half, betterhalf, the prize address, the page
caption, zero; singles and pairs) produce **zero** prize-address matches.

**Confirmed, and worth keeping:** the witness scalar `abc09ead…` uncompressed derives to
`1GSMG9VDLTU6jyuG7bkNMdmnHBLtbbM51M` — a genuine GSMG-prefixed vanity address, but not
`1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`. So the "witness operand, not the prize key" read is
exactly right, and now demonstrated rather than asserted. A "1GSMG" prefix is ~58⁴ ≈ 11M
work — cheap to grind — so the prefix alone carries no authority. This also matches the
prior S1–S4 ledger, which had already demoted that scalar.

**Per the theory's own stated pass condition** ("one miss → discard"; "only a scalar that
spends 1GSMG1JC… counts"), this branch is now closed. Recommend the community stop
spending time on XOR-of-token-hashes as a prize-key construction.

Method note retained from the writeup, and correct: only 32-byte scalars (or SHA256
digests) are XOR-meaningful. EC points, addresses and HASH160s are not XOR-closed, so
XORing those is category error regardless of theory.

Next tick: back to the primary lock — bounded three-token combos on inner96, and the
`shabef…` ("sha b4") grammar read as a construction recipe rather than as label-passwords.

### Loop tick 8 (2026-09-25) — 7×13 block claim tested; repo brought up to date

**Structural facts CONFIRMED and kept as a live lead.** The two undecoded letter blocks
have exact shapes: `dbbib…` head = **91 = 7×13**, `faed` = **570 = 6×91 + 24** (remainder
`ibibbibdcbahaidhfahiihic`). Seven identically shaped 7×13 matrices. Important: 13 does
**not** divide 570, so every earlier sweep in this ledger — which only used exact divisors
of the block length — structurally could not have found this. Genuine new ground.

**"KEY in the column sums" REJECTED as mask-overfitting.** Raw 7×13 column sums recorded in
`unverified/salphaseion_7x13_key_columns.md`; `faed[6]` reads `MERMLHQMIPIEK`, not the
claimed `DTEKEYUFFXGTD`, and no block spells KEY under any obvious sum→letter mapping. The
claim only appears after zeroing a chosen subset of source characters. Quantified the
freedom that buys: counting three-column windows that *some* mask can force to read KEY —
head 9/11, faed[1] 11/11, faed[2] 9/11, faed[3] 10/11, faed[4] 9/11, faed[5] 11/11,
faed[6] 11/11. **Every block can produce KEY in nearly every window**, so "only matrix #6"
is an artifact of which mask was searched, not a property of the data. A 3-letter word
bought with dozens of free binary choices is not evidence. To be persuasive a mask must be
fully specified in advance from the puzzle text and yield far more structure than one word.

**campaign_11_april** (~7.4k trials): issue #32's `lastwordsbeforearchichoice = april`,
`sha256(gsmg101adressapril)`, spelling variants and combos. **No hit.**

**Repo brought up to date** (the "reflect our status" pass):
- `README.md`: new "Current status of the endgame" section — the four locks with salts and
  provenance, the pinned decrypt convention, the 7×13 structural lead, and what is ruled out.
- `unverified/`: three new notes (XOR token hashes; 7×13 KEY columns; endgame password
  exclusions) + index table updated, following the folder's stated purpose of tracking
  approaches that don't work.
- `neo/README.md`: how to run the harness, and the self-test-before-trusting-negatives rule.

Cumulative logged trials: ~14.8M. All negatives trustworthy only because `aes_try.py`
self-tests the three solved blobs on every run.

Next: the `shabef…` grammar as a construction recipe; and for the 7×13 lead, look for a mask
that is *derivable in advance* (e.g. from the phase-0 colour positions) rather than fitted.

### Loop tick 9 (2026-09-25) — working the 7×13 lead

- **campaign_12** (~108k trials): the 7×13 decomposition read literally as "matrix sum
  list". Column/row/diagonal sum lists for all seven matrices, both digit bases, seven
  renderings each (digit-concat, spaced, comma, dashed, four letter mappings, total);
  concatenations across all seven and across faed's six; the seven block totals as their
  own sum list; the 24-symbol remainder; column-major reads; label-prefixed variants.
  **No hit.**
- **campaign_13** (~44k trials): a second structural coincidence — the faed remainder is
  exactly **24 symbols** and the phase-0 grid has exactly **24 coloured cells** (9 yellow,
  15 blue). That yields a mask *specified in advance by the puzzle* rather than fitted,
  which is the standard a mask has to meet to be credible. Tested: selection by colour bit
  (blue-keep and yellow-keep), zeroing by colour bit (the 2021-12-25 "zeroed out" hint with
  a pre-specified mask), XOR/add/sub/mul against the bits, the same mask tiled across all
  seven 91-cell matrices before column-summing, and label-prefixed forms. **No hit.**

The 24 ↔ 24 correspondence is kept as an observation. It may still be the right mask with
the wrong consumer — the bits were only applied to the remainder and to the matrices, not
yet to the blob-adjacent material.

Cumulative logged trials: ~15.0M.

### Loop tick 10 (2026-09-25) — primary material ingested; model corrected

User supplied an authenticated primary archive (raw page captures, verified decrypts, a
445-message creator transcript, 2026 site snapshots). Key files copied to
`neo/materials/primary/`. Findings written up in `unverified/salphaseion_soup_grammar.md`.

**Authenticity verified.** The Cosmic envelope (1344 B, salt `2d3f6fe06dc950e6`) and the
Phase-3.2 trailing envelope (96 B, salt `b45a5e3d827593ca`, offset 2292 of 2422) are
**byte-identical** to my working copies. This retires the risk that the Cosmic blob —
originally sourced from an untrusted LLM repo — was corrupt.

**Three model corrections, all creator-sourced:**
1. `yinyang` is an **output, not an input** (2025-04-28: "It's the next phase"; 2023-08-06:
   "once you hit a ying yang you'll solve it the same day"). Campaigns 01/03/05/10 fed it in
   as a password component — that was backwards.
2. The **prime hint IS the matrixsumlist hint** (2021-03-14 → points back at 2021-03-01,
   itself answering "which primes, 2/3/5/7?"). With Christmas 2021's "characters need to be
   zeroed out", matrixsumlist = zero at prime-derived positions, then sum.
3. The master hint yields **three inputs**, not seven: `yellowblueprimes`, `matrixsumlist`,
   `lastwordsbeforearchichoice`, then `yinyang` as the checkpoint.

**Soup grammar** (authoritative): `dbbi(91) | bin1=matrixsumlist | faed(570) |
agda=lastwordsbeforearchichoice | cfob=thispassword | bin2=enter | salph_inner envelope`,
salt `3ab585348552415d`, with `enter` spliced into the base64 at a `z`. So there are **two**
96-byte envelopes, and my `miniAB` reconstruction is the correct one.

**dbbi and faed are high-entropy data, not enciphered prose.** faed's 285 base-81 pairs use
75 of 81 symbols with a near-uniform profile (top counts 13,10,9,7,7,7,7…) against English's
steep profile (34,28,26,24,23…). No substitution or homophonic map bridges that. So faed
≈ 226 bytes and dbbi ≈ 36 bytes of ciphertext/compressed payload. Any theory that reads them
as English by choosing a mapping is fitting noise — this also independently re-confirms the
tick-8 rejection of the "KEY in the column sums" claim.

**New unsolved object**: `architect_span.txt`, 501 uppercase letters, IC ≈ 1.10 (random;
English ≈ 1.73). Not a short-key Vigenère/Beaufort, not present in any plaintext, and
known-plaintext key recovery against the Architect speech yields no repeating key. Parked
as its own object.

- **campaign_14** (~16.6M trials): the creator-authenticated recipe — 2016 matrixsumlist
  candidates from seven prime-derived zero masks across all seven 7×13 matrices, both digit
  bases, row/column axes, eight renderings; alone and wrapped in the other two authenticated
  components, raw and hashed. **No hit.**

Cumulative logged trials: ~31.6M.

Next: the exact zero-mask and sum rendering remain the gap. Since dbbi/faed are
high-entropy, the sum list is plausibly consumed as key material directly rather than read
as text. Also worth attacking: `architect_span.txt` as base-26 data, and the 2026 site
captures (`root_2026-08-19.html`, `followthewhiterabbit_2026-04-18.html`) not yet examined.

### Loop tick 11 (2026-09-25) — 2026 captures examined; faed/VIC pairing closed

**The 2026 site captures contain no puzzle content.** `root_2026-08-19.html` and
`followthewhiterabbit_2026-04-18.html`: no textareas, no hidden inputs, no meaningful
comments. More usefully, `followthewhiterabbit_2026-04-18.html` and
`phase1verification_2023-09-08.html` are **exactly the same byte length (36627)** with
different hashes — and a byte-diff shows the only differences are a rotating 40-char Laravel
`csrf-token` and the Cloudflare beacon's version string plus its SRI hash (164 bytes across
8 runs, all infrastructure). So **gsmg.io/followthewhiterabbit is the phase-1 verification
page served at a second URL**, not a new door. Closes the "is there a 2026 page" question.

**faed does NOT pair with the tiled VIC sentence.** Stated in advance rather than fished:
`faed` is 570 = 6×91 + 24 and the VIC plaintext is 91, so tiling VIC across faed is the one
forced analogue of the dbbi construction. Tested all three directions (faed−VIC, VIC−faed,
faed+VIC), mod 26.

| | victory words | dictionary words (len 5–9) |
|---|---|---|
| faed − VIC | none | **0** |
| VIC − faed | none | 1 (`ALVAH`) |
| faed + VIC | none | 1 (`HANDY`) |

Null over 3000 shuffles of faed's own multiset, same rule: dictionary-word count mean 1.1,
median 1, p95 3, max 7; victory words 0/3000. The real faed output scores **0**, i.e. at or
below chance. The null also shows the test has power — a planted victory word would stand
out, as it did for dbbi — so this is a genuine negative, not an inconclusive one.

Conclusion: the dbbi↔VIC pairing does not generalise to faed by tiling. Whatever faed is
operated against, it is not this. Consistent with tick-10's entropy result that faed carries
high-entropy data rather than text.

Cumulative logged trials: ~31.6M (plus non-AES structural tests).

Next: faed's operand remains unknown and must be named by primary material before testing;
`architect_span.txt` (501 letters, IC 1.10) is still unattributed.

### Loop tick 12 (2026-09-25) — OP_RETURN "script VM" hypothesis closed on logic

Proposal: unwrap `6a 47 <71B>` past the OP_RETURN, recurse into the payload (which begins
ASCII `G` = `0x47` = PUSH71), find it *exactly one byte short*, and borrow the adjacent
transaction byte — i.e. a puzzle-level state machine with the chain as program counter.

**The shortfall is forced, not a near-miss.** For payload length `L` with first byte `B`,
shortfall = `B - (L-1)`. Here `L = 71` and `B = ord('G') = 71`, so `L == B` and the shortfall
is identically **+1** for every such record and can never balance. The whole coincidence is
that a 71-byte record starts with `G` and `ord('G')`=71 — a fact about the label, not a
structural signal. JH and BH are the same format at the same length, so that is one
coincidence seen twice, not two independent ones.

**The carry bytes are inconsistent**: `0x0d` (JH) vs `0x4c` (BH), each the arbitrary first
byte of the following output amount. A real rule would give the same structural byte in both.
It also requires crossing the script-length boundary, which Bitcoin's encoding forbids, so
the rule cannot be inherited from Script — it would have to be asserted to rescue the
arithmetic.

**The other cited opcodes are ASCII artifacts**: `isolveditwithanabacus` starts `0x69` = `i`,
`secondanswer` starts `0x73` = `s`. Reading English as script always yields opcodes; that
they fail immediately is expected.

Correct in the source analysis and worth keeping: Script has no loops or EVAL; v0.1
OP_RETURN set `pc = pend`; modern Bitcoin errors immediately. No payload self-executes.
Nothing here is a vulnerability, and the proposed emulator was explicitly offline.

**Provenance caveat**: the authenticated archive lists "OP_RETURN dust" under *Excluded on
purpose*, so these records are not primary material; their length and first byte are taken
as given here, not verified.

Closed without needing the emulator. Reopening requires (a) provenance as primary material
and (b) a carry rule stated in advance giving the same structural byte across all records.

### Loop tick 13 (2026-09-25) — single-`t` mutation family closed, with control

Ran the proposed protocol exactly. **Positive control passes**: the `giveit` spelling opens
Phase 3.2 via sha256hex + EVP-SHA256 ("I've been waiting for you…"); `givetit` fails. So the
harness models the historical typo bypass, and its negatives are meaningful.

| tier | variants | trials | hits |
|---|---|---|---|
| tier 1 — insertion adjacent to existing `t`/`it` | 110 | 23,100 | 0 |
| tier 2 — insertion at every boundary | 606 | 127,260 | 0 |

**The creator settles it independently of the null result.** `giveit = givetit` is attested
(#867, #1602) — but so is its meaning: #1806 *"No clues to be found in those typos"*; #871 he
tested the whole puzzle three times with his own typo'd string, which is how it survived;
#898 *"no hints after stage 2 except the 't' to fix my stupid mistake"*; #3345 *"errors and
typos are mostly not intended"*. A one-off erratum with a published correction, not a
reusable operator. Typo-mining is ruled out at the source.

**`architect_span.txt` supplied** to the collaborator (501 letters, in
`neo/materials/primary/`). Constraints agreed: 501 = 3×167 so the only clean reshapes are
3×167 / 167×3; IC 1.10 rules out short-key polyalphabetic, so keying it against the token
list is fishing. The proposed film-transcript-difference test names a real operand, but the
film transcript is **not** in the authenticated archive, so running it would import
unattested text — flagged rather than run.

Ledger state: Bitcoin source/password battery CLOSED · OP_RETURN-as-secret CLOSED ·
giveit/givetit VERIFIED CONTROL · single-`t` family CLOSED · faed⊖VIC CLOSED ·
2026 captures CLOSED. Open: faed's operand (unnamed), architect_span (unattributed),
the grid (yellow/blue × primes).

### Loop tick 14 (2026-09-25) — the grid number frame, enumerated and closed

Published the exact authenticated coloured-cell spiral indices from
`matrix_grid_spiral_colors.json` (see `unverified/yellowblueprimes_grid_indices.md`):
blue `7 15 23 31 47 55 63 87 95 103 111 127 135 159 183`, yellow
`39 71 79 119 143 151 167 175 191`, colour sequence `BBBBYBBBYYBBBBYBBYYBYYBY`,
fefefe (7,4) = spiral index **163**.

**Corrects a circulating string**: the 25-char `BBBBYBBBYYBBBBYBBYYBFYYBY` with a spurious
`F` is wrong; the authenticated sequence is 24 chars, one per byte. Schedule-driven parses
built on the 25-char form are parsing a typo.

**Key structural point**: 1-based, every coloured index is a multiple of 8, so **none is
prime**. A prime subset exists only 0-based: `7 23 31 47 71 79 103 127 151 167 191`.

**A tempting coincidence, rejected**: there are exactly 9 primes ≤ 24 and exactly 9 yellow
cells (15 non-primes, 15 blue) — but yellow's positions intersect the prime positions only
at 5 and 19 (2 of 9). The 9/15 split is forced by the URL's LSBs, so the count match is a
coincidence of 24, not prime structure.

- **campaign_17** (66 candidates, 24,192 trials): every prime/`{2,3,5,7}` selection and
  zeroing of the URL, colour sequence and index list, both index bases; prime spiral
  indices; blue/yellow lists; sequence as 0/1 both polarities; 9/15 counts; fefefe values —
  each alone and wrapped with the other two authenticated components, raw and hashed.
  **No hit.**

Open and unchanged: whether `yellowblueprimes` consumes these indices at all, or names a
selector applied to the letter blocks with the grid only supplying the mask. Also still
open: an operand for `faed` named by primary material.

### Loop tick 15 (2026-09-25) — the YOUWON tail is not a hex key, structurally

Tested the last hopeful reading of the confirmed `dbbi ⊖ VIC` output: its 64-character tail
is exactly hex-private-key length, so does it encode one?

**No, and not because a guess failed.** A hex key written in letters requires exactly 16
distinct symbols. The tail uses **24** (A7 X5 D5 G4 B4 N4 P3 J3 U3 M3 C2 K2 W2 V2 T2 Y2 L2
E2 S2 F1 Z1 R1 O1 Q1). No injective letter→hex map exists, so every mod-16 reduction is
lossy — three letters collapse onto each digit — and whatever key emerges is an artefact of
the chosen reduction, not a recovery.

Ran three reductions regardless (A0 mod16, A1 mod16, A0 div2). All three yield valid
secp256k1 scalars; none derives the prize address. **That all three are "valid" is the
warning**: any 64-symbol string reduces to a valid scalar, so validity carries zero
evidential weight here.

Strengthens the marker reading: `YOUWON` confirms the *operation*, and the 21+64 characters
around it are residue of that operation rather than payload. The tail should not be treated
as key material again.

Closed to date: Bitcoin source/password battery · OP_RETURN-as-secret · single-`t` family ·
faed⊖VIC tiling · 2026 captures · grid prime readings · YOUWON-tail-as-hex.
Open: an operand for `faed` named by primary material; whether `yellowblueprimes` selects on
the letter blocks rather than the grid; `architect_span` (unattributed, not to be keyed).

### Loop tick 16 (2026-09-25) — "yellow brick road" reading tested

Prompted by the white-rabbit / yellow-brick-road idiom parallel. Two parts, both negative.

**Geometry.** The 9 yellow cells are not scattered: they contain a clean 4-cell diagonal
`(4,9)→(5,10)→(6,11)→(7,12)` and a 2-cell diagonal `(9,6)→(10,7)`, with `(0,13)`, `(5,6)`,
`(12,9)` isolated. A "road" reading is visually tempting.

Null-tested properly — draw 9 of the 24 candidate coloured slots (which themselves lie on
the spiral, so consecutive slots are often diagonal neighbours; the null inherits that
geometry). Over 200,000 draws the longest-diagonal distribution is
`{1: 47900, 2: 106754, 3: 35235, 4: 8418, 5: 1567, 6: 126}`, giving **P(run ≥ 4) = 0.051**.
So a 4-run occurs about one time in twenty by chance, and this was noticed *post hoc*.
Suggestive, not significant. **Not promoted.**

**Vocabulary.** campaign_18_oz, 17,850 trials: the full Oz lexicon (yellow brick road and
follow-variants, Oz/wizard/Dorothy/Toto/Emerald City/Glinda/Scarecrow/Tin Man/Cowardly
Lion/Munchkin/Kansas, "no place like home", ruby slippers, over the rainbow, the man behind
the curtain, surrender Dorothy, wicked witch), alone and combined with the authenticated
components. **No hit.**

Worth recording as a near-miss of reasoning rather than of data: the idiom parallel is real
(the puzzle's phase-1 password was itself a song lyric), but neither the geometry nor the
lexicon carries it.

### Loop tick 17 (2026-09-25) — Telegram salt re-confirmed; the 24↔24 alignment tested

**The `32656fe0…` salt is not new and not a mistype-only story.** Already analysed in
tick 3: it differs from the Cosmic salt `2d3f6fe06dc950e6` in the first two bytes only, and
— the part worth keeping — **its two ciphertexts are literal splices of the public Cosmic
blob**: `X` = cosmic ct block 8 (offset 144), `Y` = cosmic ct block 18 (offset 304). So it is
neither a second envelope nor plaintext π; it is cut-and-pasted public bytes with a doctored
salt. Re-verified this tick.

**The genuinely good structural point**, and it is parameter-free:

```
dbbi length            = 91
primes <= 91           = 24   (2 3 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89)
coloured cells         = 24   (15 blue, 9 yellow)
```

The 24 colour bits map one-to-one onto the 24 prime positions of dbbi. That is
`yellowblueprimes` and "some characters need to be zeroed out" as a *single* instruction with
nothing free to tune — much better motivated than any mask tried so far.

Built it. The only variation is unavoidable convention (index base, which colour zeroes,
digit base, axis, rendering) plus "add/sub, not replace".

- **The cited strings do not reproduce.** Neither `RUSHMLKVTGIAG` nor `PVYWIAEEYKNAZ`
  appears under any of the 16 parameter-free variants of this construction. They were
  computed some other, unstated way, so they are **not** verified operands and the
  "yin/yang pair" framing around them is not established. The 16 strings this construction
  actually yields are recorded in the tick output (e.g. base0/zeroY/b1 col A1 →
  `BFIFXGOHAFXZL`).
- **campaign_19** (2352 candidates, 409,920 trials): the mask across dbbi and all six faed
  matrices, both bases, either colour zeroing, both digit bases, zero/add/sub modes, row and
  column axes, seven renderings. **No hit.**

So the best-motivated mask in the session is enumerated and empty. Recorded because the
alignment is real and someone will rediscover it; the negative is the useful part.

Also filed per that note, and consistent with this ledger: the 12:00 photo is Reloaded lore
(the 314-second window, the midnight shift change), not a grid operand, and neither it nor
the doctored header enters the password battery.

### Loop tick 18 (2026-09-25) — the two recurring claims, measured

Agreed with the five verdicts (corridor gloss = film flavour; the "impossible to decrypt"
quote is unverified and contradicts the 2023 hint; "source is raw data" is already on the
board as DBBI/FAED; "3.2 → 32" is filename numerology; window=32 / IV=0 drops). Made two of
them quantitative — see `unverified/why_false_decrypts_recur.md`.

**The IV is KDF-emitted.** For the known-good Phase-3.2 decrypt, EVP_BytesToKey emits
key `f4c72c3a…` *and* IV `b620574d04ee253df257fcd340eb201f`. Not chosen.

**Important nuance that makes zero-IV claims look credible**: the correct key with a zero IV
still prints ~94% readable text, because in CBC a wrong IV corrupts only the first 16-byte
block and the stream self-heals from block 2. So a zero-IV "decrypt" can look like a hit and
is not one. The decisive direction is the converse — a wrong key gives nothing readable for
any IV — so "IV = 0" is not a construction: it still requires naming the 32-byte key, which
is the entire problem.

**Padding is a 1-in-256 coincidence, measured**: against the real 80-byte ciphertext with
random keys, 300,000 trials gave **1,235 PKCS#7-valid** results (1 in 243; theory ~1 in 256)
and **0** that also passed this harness's gate. So a 100k-candidate battery throws ~400
padding-valid results by chance — the complete explanation for the recurring Cosmic
"decryptions", and a validation of the pad≥4 / magic / printability rule.

Rules of thumb now on record: a 1-byte pad with a non-printable body is noise, always; a
claim that names an IV but not a key has specified nothing; and "it yields a valid
key/padding/address" is never evidence, since every 64-symbol string gives a valid scalar
and 1 in 256 keys gives valid padding.

### Loop tick 19 (2026-09-25) — provenance pass: instructions, not coincidences

Agreed with the demotion of `RUSHMLKVTGIAG` / `PVYWIAEEYKNAZ` (reproducible ≠ compelled;
I could not reach them from any parameter-free construction, and the stated chain fixes a
digit map `d=0,b=1,i=2,f=3,h=4,c=5,e=6,g=7,a=8` that is itself a choice). Skipped the
redundant add/sub rerun — campaign_19 covers it. Ran the provenance pass instead.

**Only 10 of 510 rows are creator-authenticated (HINT/CONFIRM) on prime / zero / yellow /
blue / matrixsumlist / dbbi / faed / yin-yang across seven years**, and the archive's own
tags separate them into three scopes:

| thread | tag | when |
|---|---|---|
| yellow / blue | **P0** | 2020-01 poem, 2020-05 "answer is there", 2020-05 "First or zero" |
| primes / matrixsumlist | **SAL** | 2021-03 prime part, 2021-03 matrixsumlist→prime hint |
| the combined list, yin-yang | **COS** | 2023-02 master binary, 2023-08, 2025-04 |

**The overlooked item**: `#4105 2020-05-21 HINT "First or zero"`, tagged P0, immediately
after `#4102 CONFIRM "answer is there"` and `#4096` re-pointing at the poem. Two live
readings — (a) it answers "Yellow has a number and so does Blue" with **1 and 0**, or (b) it
disambiguates "first puzzle piece" = "phase zero". Under either, **`yellowblueprimes` is not
licensed to mean "9, 15, primes"; under (a) that is positively excluded.**

Consequences recorded in `unverified/creator_hint_provenance.md`:
- The 9/15 counts have **no creator warrant**. Every construction here that fed `9`/`15`/
  `915`/`159` used a community inference, not an instruction.
- `yellowblueprimes` as one atomic operator is unsupported — the token occurs once, inside a
  2023 list that otherwise names already-solved stages and is followed immediately by
  "we wont give away the password / it's in front of your eyes". That list reads as a
  **table of contents**, not a recipe.
- The prime instruction is scoped to **SalPhaseIon**, anchored only by the 2021-03-01
  2/3/5/7 exchange plus 2021-12-26 "some characters need to be zeroed out".

Ledger per the agreed state: CLOSED adds prime-cell add/sub (covered by campaign_19).
DEMOTED adds RUSHMLKVTGIAG, PVYWIAEEYKNAZ, and 24→24 insertion-from-equal-lengths.
OPEN: exact DBBI decoder, exact FAED decoder, and now — sharpened — what the P0-scoped
yellow/blue answer actually contributes, given it is not counts.

### Loop tick 20 (2026-09-25) — stage chaining tested and closed

Agreed on the OpenSSL analysis (independently proved last tick: the `Salted__` magic is
written only in password mode, so a password provably exists and the IV is not a free
input). Held position on the third-door oracle: that address is absent from the
authenticated archive — which excludes that dust family by name — and hunting an unknown
preimage by hashing candidates is brainwallet grinding regardless of intent. Not built.

**Outside-the-box test actually run**: the one *confirmed* operation is `dbbi ⊖ VIC`
(planted YOUWON, 0/200k null). Chained puzzles normally feed a stage's output forward as the
next stage's key — and stage 1's outputs had never been used that way. So:

```
stage 1 (confirmed): VOZIJBDTIQBRGVEOMZNBC YOUWON XCPKW…QTSGA
                     [--- prefix 21 ---]        [--- tail 64 ---]
stage 2 (new test):  faed(570) ⊖ / ⊕ {tail64, prefix21, full91, YOUWON, + reversals}
```

Operands named in advance; all six keys × two directions.

| | dictionary words | special |
|---|---|---|
| best variant (tail64, sub) | 1 | none |
| null (3000 shuffles of faed, same rule) | mean 1.0, median 1, p95 3, max 6 | 3/3000 |

Real sits at the **37th percentile** of its own null — indistinguishable from chance. The
null also shows the test has power (special words appear in only 0.1% of shuffles), so this
is a genuine negative. **campaign_20_chain** additionally fed all 48 stage-2 outputs (plus
lowercase and first/last-64 slices) to the locks: 10,080 trials, no hit.

So stage chaining is closed: the YOUWON output does not key faed. Combined with tick 15
(the tail is not a letter-encoded hex key, 24 distinct symbols vs 16 required) and tick 11
(faed does not pair with tiled VIC), the confirmed dbbi operation appears to be
**terminal** — a marker, with no forward link discovered from any of its outputs.

Running total ~32M logged trials. OPEN remains: the exact FAED decoder, and what the
P0-scoped yellow/blue answer contributes given the provenance pass showed it is not counts.

### Loop tick 21 (2026-09-25) — the π chain verified, quantified, and traced to a dead premise

**Every arithmetic step in the proposed chain is correct.** Verified independently:
9th prime = 23, 15th prime = 47, π[9] = 3, π[15] = 3, π[23] = 4, π[47] = 7. No errors.

**But π[9] == π[15] is a 10% coincidence.** Among the first 200 fractional digits, equal
pairs occur 1968/19900 = **9.9%** — π digits are ~uniform, so *any* two positions match about
one time in ten. "They are both 3" is therefore an ordinary event, and the déjà-vu / glitch
reading is a narrative fitted after seeing it. The follow-on `π[23]=4, π[47]=7 → "47"`
recurring as the 15th prime is self-reference selected post hoc: the chain was extended until
something repeated.

**The load-bearing failure is upstream of all of it.** The chain starts from Yellow = 9,
Blue = 15 — the *cell counts*. Tick 19's provenance pass found those counts have **no creator
warrant**: the 2020-05-21 HINT "First or zero" (tagged P0) follows the poem and "answer is
there", and the colouring independently just restates the URL's own byte LSBs. If "Yellow has
a number" resolves to **0/1** rather than 9/15, then primes(9), primes(15), π[9] and π[15]
all inherit nothing. Each step is valid; the input is not established.

**The raw-K/IV experiment — genuinely different, and run.** Not a password battery: direct
AES-256-CBC(K, IV) with no KDF, no salt derivation, strict gate (padding alone never
accepted). 23 source-derived 32-byte keys × 20 source-derived 16-byte IVs × 4 targets
(P32T ciphertext and whole file, cosmic ciphertext, miniA ciphertext) = **1,840 direct
decrypts, 0 hits.**

Key material drawn only from authenticated two-part objects: sha256 of each decoded token,
the VIC sentence, the confirmed stage-1 output, dbbi, faed, the 24-bit colour mask and the
196-bit grid, both 32-byte cosmic halves, and zero. IVs from sha256/md5 of the same, the
colour bits, doubled salts, and zero.

So the raw-key model is now tested rather than merely doubted, and it is empty on this
material. Combined with tick 20's proof that the `Salted__` magic is emitted only in
password mode, the password path remains the only one with positive evidence behind it.

### Loop tick 22 (2026-09-25) — π as raw key/IV: exhaustively closed

Ran the proposed test as a **superset** of the suggested script. That script checked roughly
30 combinations (offsets 0/9/15/23/47) and accepted on `unpad` alone — i.e. PKCS#7 only,
which tick 18 measured at a **1-in-243 false-positive rate**, so it would have reported
spurious successes at scale.

Instead, exhaustively, with the strict gate:

- π computed locally to 1200 digits (spigot, no external data)
- both the fractional expansion and the full `3.`-prefixed form
- both byte interpretations: ASCII digits, and digits packed as nibbles
- **every** key offset 0–199 × **every** IV offset 0–199, not just the five proposed
- 4 targets: P32T ciphertext and whole file, cosmic ciphertext, miniA ciphertext
- plus sha256 of π prefixes at 6 lengths as key, against 5 IV offsets

**640,480 direct decrypts, 0 hits.**

So the family is closed far beyond "simple ASCII π segments": no offset of π, in either
digit encoding, as key and/or IV, opens any lock.

**Two corrections to the proposed method, both worth keeping:**

1. `unpad`-only acceptance is not a success criterion. Padding alone is a 1-in-243
   coincidence on these ciphertexts; a sweep of this size would have thrown ~2,600 false
   "successes" under that rule. The gate must require pad ≥ 4, a ≥4-byte magic, or high
   printability.
2. The "re-insert a dummy `Salted__` header and brute-force the password" step **cannot
   work**, and not merely because P32T already has a real header. The salt is an *input* to
   `EVP_BytesToKey(password, salt)`. Substituting an invented salt derives a different key,
   so the original plaintext is unreachable no matter how many passwords are tried; you
   would additionally have to brute-force the true 8-byte salt (2⁶⁴).

Endorsed without reservation: **do not execute unknown binaries.** Decrypting data is safe;
running what comes out is not. Static analysis only, and an isolated VM if it ever comes to
that. Nothing in this repo requires running third-party code.

### Loop tick 23 (2026-09-25) — the déjà-vu / 314 glitch, taken literally and closed

Took the film metaphor to its one genuinely cryptographic meaning. **A glitch in the Matrix
is seeing the same thing twice; in a ciphertext that is a repeated block.** Under CBC with a
random IV a repeat is ~2⁻⁶⁴ per pair, so finding one would be real signal — it would mean
ECB, or a reused IV/keystream. That is a proper test, not a metaphor.

**Result: no duplicate blocks anywhere.**

| blob | blocks | distinct | duplicates |
|---|---|---|---|
| cosmic ct | 83 | 83 | **0** |
| P32T ct | 5 | 5 | **0** |
| miniA ct | 2 | 2 | **0** |
| miniB raw | 3 | 3 | **0** |

So the envelopes are well-formed CBC with no structural anomaly. There is no glitch in the
ciphertext to find, which also independently re-confirms they were not made in ECB.

**314 as a position**: nothing distinguished. `cosmic[314]`, `faed[314]='c'` (`ichi` in
context), soup`[314]='a'`. **314 as a window**: faed admits 314-length slices at offsets
0–256; their IC is flat (min 1.043, median 1.088, max 1.124), so no window is a real
segmentation. **Longest repeated substrings**: dbbi `egge` (4), faed `aedgg` (5) — short, as
expected from the earlier entropy finding.

**campaign_21_pi314** (17,220 trials): 314 / π / window-of-opportunity / déjà-vu / black cat
/ 12:00 / midnight / shift-change / Keymaker / corridor / two-doors vocabulary, alone and
combined with the authenticated components. **No hit.**

With tick 22's exhaustive π-as-key/IV sweep (640,480 decrypts) this closes the π/314 thread
in all three of its forms: as key material, as an index, and as the déjà-vu structural
signature. The metaphor is film flavour; the ciphertexts are ordinary well-formed CBC.

### Loop tick 24 (2026-09-25) — the π-handle "0b1one|" claim: unverifiable, and its own test fails

**Cannot verify the premise.** The Telegram handle renders in *every* screenshot supplied as
`3.14159265358879323846264338327...` — 29 fractional digits before Telegram's ellipsis. The
claimed insertion sits after fractional digit **50**, i.e. beyond the truncation in all
available images. Nothing in the material shows `0b1one|`. (The claim's π arithmetic is
right: digits 1–50 are correct and the true continuation is `5820974944592…`.)

Even granting it: a participant's display name is not authenticated puzzle source, as the
claim itself concedes.

**The proposed test was run and returns negative.** The suggested criterion was: does `11`
occur independently in authenticated material in the Phase-0 / prime / zeroing chain? It does
not. That chain supplies **9, 15, 24, 91, 196, 570** — no 11. The only `11` in authenticated
material is inside phase-2.2 part 5 `11110`, a 5-bit string already consumed as a solved
component of the phase-3 password; its `11` is a substring of a bitstring, not an independent
quantity.

**And the other half is already demoted.** The `9` comes from Yellow = 9, which tick 19's
provenance pass showed has no creator warrant — "First or zero" (2020-05-21, P0) points at
0/1, and the colouring independently restates the URL's own byte LSBs.

**campaign_22_911** (12,180 trials): `911`, `9:11`, `0b1one`, `0b1`, `one`, `oneone`, `11`,
`nineeleven` and variants, alone and combined with the authenticated components. No hit.

So by the claim's own stated standard — *"if it does, 9:11 stops being dependent on personal
recurrence and becomes source-derived"* — the condition is not met.

### Loop tick 25 (2026-09-25) — "what two numbers?" — the creator answered it

Ran the proposed enumeration: canonical scalar summaries of the authenticated blue/yellow
sets, then only prime-licensed operations, with an explain-something-authenticated gate
before any ciphertext. Also flagged the correction that the ledger was missing.

**The creator answers the question directly.** The chain is one P0 thread:

```
2020-01-14  HINT     "Yellow has a number and so does Blue. Go back to the first puzzle piece"
2020-05-20  META     re-points to that poem as THE hint
2020-05-21  CONFIRM  "answer is there"
2020-05-21  HINT     "First or zero"        <- tagged P0 HINT2020
```

Four months after posing it, in the same thread, he says **"First or zero"**. That is the
most direct available answer to "what exact two numbers?", and it says **1 and 0** — not 15
and 9. It also matches what Phase 0 already uses (blue=1, yellow=0) and the independent
finding that the colouring merely restates the URL's own byte LSBs. So `blue count = 15` /
`yellow count = 9` should move from AUTHENTICATED to *derived measurement* — true of the
image, but not what the hint is pointing at.

**The enumeration** (all ten summaries):

```
blue.count 15   sum_urlbyte 142  sum_spiral 1241  sum_row 98  sum_col 73
yellow.count 9  sum_urlbyte 134  sum_spiral 1135  sum_row 58  sum_col 83
```

Prime-licensed results: `15 → 15th prime 47`, `9 → 9th prime 23`; neither 47 nor 23 is an
authenticated quantity of this puzzle. `15+9 = 24` matches the coloured-cell count, but
trivially — there are 24 cells, so the sum of the parts is the whole; it explains nothing.

**Gate result: nothing explains an authenticated quantity it did not start from.** The family
is closed without touching a ciphertext, exactly as proposed.

One honest observation, not promoted: both column sums are prime (blue 73, yellow 83). Around
that magnitude prime density is ~1/4.6, so both being prime is ~1/21 — and it is 2 of 10
summaries, i.e. selected after looking. Recorded, not elevated.

Agreed and filed: `15/9 → O/I → Base58` is analyst-created; the `2,3,5,7` enumeration is a
solver's characterisation rather than primary text (the authenticated statements say only
that primes are required and important); and the π-handle content cannot supply an operand
unless the account is shown to be creator-controlled.

### Loop tick 26 (2026-09-25) — the proposed pipeline is complete; final stage run

A six-stage pipeline was proposed. Five stages were already executed in this session; the
sixth (Bitcoin v0.1 constants) was genuinely untested and is now run. Status:

| stage | status | result |
|---|---|---|
| Header check (`Salted__`?) | done (tick 20) | **YES** on all locks — and the magic is emitted *only* in password mode, so a password provably exists |
| Raw AES-256-CBC, no KDF | done (tick 21) | 1,840 direct decrypts, source-derived K/IV — 0 hits |
| π candidates (ASCII/nibble, offsets, sha256 slices, déjà-vu) | done (tick 22) | **640,480** decrypts — all offsets 0–199 × 0–199, both encodings — 0 hits |
| Matrix glitch / duplicated values | done (tick 23) | 0 repeated blocks in any blob; 314 not distinguished as index or window |
| **Bitcoin v0.1 constants** | **new this tick** | genesis hash, merkle root, nonce 2083236893, timestamp 1231006505, bits 0x1d00ffff, version, coinbase string (and its reversed/hex forms as used in phase 2.2 part 6), genesis address, satoshi/nakamoto vocabulary — **13,020 passphrase trials + 792 raw-K/IV decrypts, 0 hits** |
| Static analysis of binaries | N/A | no binary exists in the corpus; nothing to analyse |

The Bitcoin-constants stage was the best-motivated of the untested ones, since phase 2.2
part 6 provably used the genesis coinbase message (hex-encoded, reversed). Testing the same
family again at the endgame was reasonable. It is empty.

**Answer to the proposed immediate check** (`xxd -l 64 p32t.enc`): the file begins
`53 61 6c 74 65 64 5f 5f` = `Salted__`, followed by salt `b45a5e3d827593ca`, then 80 bytes
of ciphertext. Per tick 20 that *settles* the branch rather than opening it: raw `-K/-iv`
mode writes no header at all, so the header's presence is positive evidence of the password
path, not a reason to pursue raw keys.

Cumulative ~33M logged trials across 23 campaigns. The pipeline is exhausted; the open work
remains the FAED decoder and the bit-selector reading of yellow/blue implied by
"First or zero".

### Loop tick 27 (2026-09-25) — zero-injection decode of faed/dbbi: negative

Best remaining source-grounded lead, run. Logic: faed and dbbi use letters **a–i only**
(no `o`), while the sibling tokens `agda`/`cfob` decoded with the map `o=0, a=1…i=9` →
concatenate digits → decimal int → hex → ASCII. So "some characters need to be zeroed out"
may be the instruction that *injects* the missing `o` (zero) into faed/dbbi, after which the
same sibling decode could apply.

Tested: zero-inject at prime positions (0- and 1-based, prime and non-prime), and at the 24
colour-bit positions mapped to the 24 primes ≤ 91 (both polarities), then the exact
agda/cfob decode. **Every result is ~33–45% printable — garbage.** No readable text, no token,
no structure. faed and dbbi remain high-entropy under this transform too, re-confirming the
tick-10 entropy result.

This was the last well-motivated, source-named decoder hypothesis on the board. With it
negative, the honest state is that **no source-named operand or decoder for faed has been
found**, and the confirmed dbbi operation (⊖ VIC → YOUWON) is terminal (tick 20). The puzzle
is not solvable from the material in hand by the systematic methods available in this session.

### Loop tick 1b (2026-09-25) — 2×14 board coordinates vs P32T, preregistered and parked

Ran exactly as preregistered: narrow, P32T-only (salt b45a5e3d827593ca), two fixed boards
reported separately and never blended, no new vocabulary, strict gate, Cosmic excluded.

Boards (2 rows × 14 cols):
- A = `FUBCDORA.LETHINGKYMVPS.JQZXW`
- B = `fubcdora/lethingkymvpszjqwx.`

**Step 1 — removed-material selector** (`KING`, `QUEEN`, duplicate `C`, then `KING||QUEEN||C`
and `QUEEN||KING||C` only). Coordinates in word order, serialized as: column 0/1-based, row
bits, interleaved (row,col) 0/1-based, packed coordinate bytes, decimal-ASCII, board-char
control. Each raw and sha256hex, × EVP-{md5,sha256}.

**Step 2 — checkerboard numbering** (two rows → two straddling-checkerboard branches, columns
→ 14 positions; both row assignments; digit-ASCII, nibble-packed; no arbitrary digit perms).

Protocol: candidate → {raw, sha256hex} × EVP-{md5,sha256} × P32T only. Strict PKCS#7 +
structure gate.

**Result: 182 trials per board, 0 hits, 0 near-misses. Both boards negative.**

Per the preregistered stop rule — "if both removed-material coordinates and canonical
checkerboard numbering miss under this frozen protocol, park the chess-board/P32T branch" —
**the chess-board/P32T branch is parked.** The 2×14 observation (VIC sentence is 91 chars = the
dbbi length; the 28-symbol alphabet is 2×14) remains structurally elegant but yields no
justified next reading rule. Not blended, not widened, not re-run with new vocabulary.

### Loop tick 28 (2026-09-25/26) — Cosmic closure of the tick-1b set; the constraint sheet; the genesis image re-read

**1. The tick-1b token set against Cosmic — closed.** The requested "57-token" list is not in
this repository (the ledger records tick 1b as 182 trials per board, and the campaign_24 logs
are empty because only pad-valid results are logged), so the set was regenerated from
`campaign_24_board.py`: **50 distinct raw candidate strings** (the two boards share every
coordinate, so their union is one set; written to `neo/attempts/campaign_25_tokens.txt`).
Protocol exactly as requested: each token raw and as sha256hex × EVP-MD5 and EVP-SHA256 ×
Cosmic only (salt `2d3f6fe06dc950e6`, ct 1328 B), strict gate.
**campaign_25: 200 trials, 0 hits, 0 pad-valid results.** If the user's 57 contained tokens
outside tick 1b, those seven were never in this repo and must be supplied; everything that
was here is now closed against Cosmic as well as P32T.

**2. Constraint sheet written and fact-checked** — `unverified/endgame_constraint_sheet.md`.
Operands, operators and representations per official hint, each graded (AUTH / PRIMARY /
DECODED / DERIVED / READING / LORE-BANTER-META / APRIL / USER / NEGATIVE / POLICY), with
frozen tables B0–B3 and C0–C3. Five independent refuters attacked the sections against the
primary files; the substantive corrections (all folded in):
- the sheet had labelled artefacts and interpretations AUTH; a PRIMARY grade and a READING
  grade now separate "the creator said" from "the archive contains" and "we read it as";
- `yinyang`: the three creator lines make it a *phase reached after the wall* (#9599, #39224,
  #39237); "output of a decryption / not an input" is our reading of them. The combine row
  now reads `A‖B‖C` — the earlier draft fed D back in, the exact pattern correction 1 retracted;
- "First or zero" (#4105) has no preserved question; three readings stay live (1/0; phase
  zero; index base), so the 9/15 counts are unlicensed rather than excluded;
- primes: the AUTH content is only "required"; the selector model is a reading, and the tie to
  `matrixsumlist` rests on the META reply context of #6509;
- `{1},{4},{21}` is archive-tagged HINT and downgraded to APRIL by the sheet (#7529, #6913
  "1812 bit" = RAB-bit); #70307 "Pfff. Coincidence." reacts to an unarchived solver post and
  neither confirms nor denies anything;
- the close-friends hint is #66573/#66574 (HINT, tag KEY, 2026-07-13): friends' knowledge
  *plus* skill, not "biographical rather than technical".
Every numeric value in the operand table reproduces (spiral, colour indices, 0xF73D92, sums,
91/570/24, the dbbi−VIC string, the 24 primes).

**3. The genesis image, whole.** `puzzle.png` is byte-identical to the archive's
`02_pages_raw` capture (sha256 `38125bbd…`), and it is 1048×1556, not a bare grid:
- the QR code decodes to `https://www.blockchain.com/btc/address/1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`
  — the prize link, nothing hidden;
- the **rabbit** is pixel art on a 15-px lattice, 14 × 13 lattice cells, 37 black pixels,
  drawn over cells (6,6),(6,7),(7,6),(7,7),(7,8),(7,9),(8,6). The spiral's four unused end
  cells are exactly (6,6),(7,6),(7,7),(6,7): the poem's "rabbits nest" is the spiral's centre.
  Read as bits under every attested encoding (row/column order, both polarities, bit- and
  byte-reversed) it yields no printable output (best 0.32). It is a drawing. Saved as
  `neo/materials/rabbit_bitmap.txt`;
- the colours have literal numbers: yellow `#FFF200` (2⁹·181²), blue `#3F48CC`
  (2²·3·37·9341), the red rule `#ED1C24`, the off-white `#FEFEFE` (2·3·7·13·127·241). A
  fourth reading of "Yellow has a number and so does Blue", never tested here before.

**4. Bounded offline address oracle** — `neo/harness/addr_check.py`: six fixed encodings
(sha256, sha256d, hex64, zero-padded raw, bit-reversed sha256, byte-reversed sha256) ×
compressed/uncompressed, against the prize address, the README second address and the
user-supplied `1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9` (USER grade: absent from the archive;
block explorers are egress-blocked, so its history is unverified). Capped at 2000 objects
per run so it stays an oracle for named objects, not a grinder.
- campaign_26: every object named in the sheet (49) → 458 addresses, **0 matches**;
- campaign_27: the colour codes in hex/decimal/packed, singly and yellow‖blue / blue‖yellow
  (34) → 340 addresses, **0 matches**.

### Loop tick 29 (2026-09-26) — the Base58 frame, verified and closed

User frame: soup letters `a…i` are Base58 glyphs 33–41, not digits, when the object is a
Bitcoin value; the puzzle's numbers should be written in Base58; slot A is the colour
integer `f73d92`, not a spelling of `yellowblueprimes`; "zeroed out" = delete the
Base58-illegal set `{0,O,I,l}`; Base58Check is the only encoding the prize wears in public.

**Arithmetic verified** (validated against the canonical Bitcoin alphabet):
- row sums `610876654997879` → `5mfhF9tp6`; col sums `8108108736759668` → `26KBGX9uKH`;
  rows‖cols → `7RUyS4gBTMenM76Fcf`; `f73d92` = 16203154 → `2S3dj`; prime-subset `445` → `8g`.
  All match.
- **One correction**: the complement (Y=1,B=0) `574061` encodes to **`3wec`**, not the
  stated `3Q9h`. Used `3wec`.
- `yeowbueprimes` (label minus `l`) is legal Base58 and decodes to
  `82101348098033013316316` = 10 bytes `1162b9166f936e795adc`; reproduces the user's value.
- **Whole-block Base58Check fails** for `dbbi` (91→67 B) and `faed` (570→418 B): both are
  legal Base58 strings but neither is a valid version+payload+checksum. So neither block is a
  hidden address/WIF. Confirmed; do not slice them for a `1…`/`5…`/`K…` prefix.

**campaign_28_base58 — the bounded test, run through the self-testing harness.**
Slot A = the colour integer in every representation (`f73d92`, `F73D92`, `16203154`,
`0xf73d92`, `2S3dj`, the complement `08c26d`/`574061`/`3wec`, the prime-subset `445`/`8g`/
`110111101`, the zeroed label `yeowbueprimes`/its decimal), plus a "delete `{0,O,I,l}`"
variant of every slot value. B and C = the frozen sheet sets and their Base58 forms.
Combine A‖B‖C (the §6 join), each raw and sha256hex, EVP-MD5 and EVP-SHA256, against
**cosmic, inner96 (P32T) and miniAB (salph_inner)**: **1672 combine candidates + 19 A-alone,
20,292 trials, 0 hits, 0 pad-valid near-misses.** Address oracle on the A family and each
`A‖matrixsumlist‖lastwordsbeforearchichoice`: 342 addresses, **0 matches** to prize / second
/ `1NULY7`.

So the colour integer as slot A, in every Base58/hex/decimal/zeroed representation and
combined with the frozen B and C, opens no lock and derives no target address. The Base58
*representation* frame is closed. Base58 stands only where it is actually attested: as the
last-mile dress of the answer (WIF `5`/`K`/`L`, or `1GSMG1…`/`17ucy1…` from a hash160), i.e.
an oracle for a real hit, not a way to brute the blob. What is still missing is unchanged: a
*further named operation* on `f73d92` (the SAL-scoped primes/zeroing) that yields a
recognisable object before AES — not another spelling of the label.

### Loop tick 30 (2026-09-26) — the P32T last-block freeze oracle; the two halves; a reading tension

User frame: P32T is 80-byte CT, 5 CBC blocks; the last block `P5 = D_K(C5) XOR C4` depends
only on K (C4, C5 are known ciphertext), so it is an **IV-free** test. If the plaintext is
two raw 32-byte keys (64 B content), `P5 == 0x10 * 16` — a 128-bit accept test, far sharper
than the 1-in-243 PKCS#7 filter. Stop hashing VIC strings; find the *operation* on the two
named halves (HALF / BETTER HALF = the on-chain `1GSMG1…` and `17ucy1…`), not another spelling.

**Built `neo/harness/p32t_freeze.py`** — the IV-free oracle, self-tested (accepts the key that
padded a synthetic 64-byte plaintext, rejects a wrong key). `C4 = d9f7ff6e…`, `C5 = 5334de08…`.

**A reading tension the freeze surfaced, and resolved into a fuller oracle.** `0x10*16` tests
only the 64-byte reading. The repo's own primary reading of P32T is "64 hex chars + a
newline" = **65** bytes, whose last block is `0x0a || 0x0f*15`, which the `0x10*16` test would
reject. So a key correct under the hex+LF reading would look like a miss. The oracle now tests
every IV-free last-block reading: `64B-tworawkeys` (`0x10*16`), `65B-hexkey+LF`
(`0x0a‖0x0f*15`), `65B-content+pad15`, and any shorter valid PKCS#7 pad (logged, weak).

**campaign_29_halves — K from the two public halves, plus a named-object sweep.** Public
bytes only (no VIC word strings): `hash160(1GSMG1…) = a9553269…`, `hash160(17ucy1…) =
4bc46844…`. 42 one-rule keys — `sha256` of the two hash160s / version+hash160 / 25-byte
payloads / address strings, both orders and space-joined, `sha256(A)⊕sha256(B)`, double-sha,
raw concatenations trimmed to 32, hex-string forms — plus EVP-{MD5,SHA256} of the address
strings with the P32T salt. Then 12 named 32-byte objects as `sha256(object)`.
**50 candidate keys, 0 strong-reading hits, and 0 that produce even a chance valid pad** in
the last block (random keys give one ~1 in 255, so 0/50 is noise, no signal). Per-candidate
P5 logged in `neo/attempts/campaign_29_halves.jsonl`.

**Conclusion (the honest revelation, a sharp negative that redirects).** Under a clean,
reading-aware, IV-free 128-bit oracle, P32T's key is **not** any public-byte formula on the
two halves, nor `sha256` of any named object, nor (per the user's own runs) any VIC-string
KDF. Combined with tick-20's proof that `Salted__` is written only in password mode and the
tick-29 Base58 closure, **P32T is not opened directly from any currently-named object.** The
arrow reverses: an earlier step (Cosmic, or the still-missing slot-A operation) must name
P32T's operand first. The missing piece is the operation, and it is now shown not to be a
public-address derivation either. No AES campaign on P32T or Cosmic is warranted until a
primary statement names an operand that is not a VIC string — which the archive does not
currently supply. The freeze oracle stays as reusable tooling for any future K.

**Salt-structure probe (same tick).** The salt is the one field the creator chooses freely
at encryption time, so it is a natural place to plant a pointer. Examined all six real salts
(the three unsolved locks + the three solved stages) for ASCII, byte-reversal, pairwise XOR,
digit/base structure, and repeats: **nothing.** No salt is printable, no reversal or XOR
yields text, byte distributions are chance (the one repeated byte in the salph_inner salt is
within the ~11% birthday chance for 8 bytes). The salts are ordinary random OpenSSL salts;
they carry no operand. (Re-confirmed the TG-doctored salt differs from cosmic only in bytes
0–1, tail `6fe06dc950e6` shared — a splice, as tick 3 found.) So "the salt names the next
step" is closed.

### Loop tick 31 (2026-09-26) — forensic/provenance round: five channels audited, all dry

Per the standing plan (no more AES batteries; find the named operation or a new artifact):

**1. P32T reading made canonical.** The repo asserts the **hex-key+newline** reading (README:
the 80-byte CT "fits a 64-character hex private key plus a newline") = 65 B content, pad 15,
so PRIMARY `P5 == 0x0a‖0x0f*15`; the two-raw-keys reading (64 B, `0x10*16`) is SECONDARY.
`p32t_freeze.accept(K)` now checks primary, then secondary, then any valid pad. No future key
will be rejected for the wrong length assumption.

**2. `4943` audit — coincidence, closed.** `f73d92 = 2·11·149·4943`; `4943` was the only
unexplained residue. It is prime; it appears **literally nowhere** in any authenticated text;
**no puzzle object is even 4943 bytes long** (page 2150, soup 2149, architect 501, cosmic
1344, phase-3.2 2422), so offset/line/index-4943 readings do not apply; modular coords
(mod 196 = 43, mod 91 = 29, mod 58 = 13, mod 24 = 23, mod 14 = 1) name nothing. A 24-bit
colour field's prime factorisation carries no puzzle meaning. Closed as coincidence; not hashed.

**3. Named-operation audit — no statement names an endgame operand.** Every HINT/CONFIRM with
an operation verb (hash #225/#226, the giveit fix #867, HASHTHETEXT/Decentraland, zeroing
#8000, binary reversal #8446, split half/better-half, index {1,4,21}/primes) attaches to a
solved or upstream stage. **No authenticated statement names P32T, salph_inner, inner96, the
envelope, or the Cosmic blob as the object of an operation**, nor any operation that produces
32-byte material from an already-named object. The Cosmic HINT/CONFIRMs (#8311/#8315/#8328)
point at the Time-Life "Cosmic Duality" book cover being "scary specific", not at an operation
on the blob. The live gap (an earlier step must name P32T's operand) is unfilled by the archive.

**4. Git forensics for S0 — not recoverable.** One branch, no stashes/tags; deleted files in
all history are only the untracked `__pycache__` bytecode and two old `phase2.png`/`phase3.png`.
A full blob scan of every object in history finds seed material only in the already-known
parked `neo/prior-sessions/2026-09-25-S1S4/` files; no hidden or deleted S0. S0 remains the
uninvertible SHA256 preimage of head S1 — confirmed unrecoverable, as the parked ledger stated.

**5. Matrix oddities — unnamed, kept as markers.** No primary sentence names the near-white
`#FEFEFE` cell (7,4) or the 4-bit spiral residue `0000`. "White" occurs only in the poem's
"Roses are White" line; the creator explicitly claims **no hidden picture** in the rabbit
(#23200 "Squares and a rabbit?… no hidden picture"); the one gaze theory (#2905 "rabbit
looking to this point") got a non-committal "Interesting 😜". Both oddities stay markers.
(Observation, not promoted: the rabbit is drawn in cells cols 6–9/rows 6–8 and `#FEFEFE` sits
at (7,4), to its left; a left-facing rabbit would "look toward" it. Post-hoc geometry, and the
creator was non-committal — recorded, not elevated.)

**6. Salt exclusion** recorded in tick 30 addendum: six real salts, no ASCII/reversal/XOR/
structure, no pointer. Reusable closure of the salt channel.

**7. Stop.** All six forensic channels are dry and no new operand appeared. Per the plan, no
further AES campaign is run: the measured false-positive regime would manufacture noise, not
answers. The impasse breaks only with a new authenticated artifact naming the operation, or
the lost S0 seed — neither available. The freeze oracle and the address oracle remain as
tooling for any future candidate key.

### Loop tick 32 (2026-09-26) — the f73d92 factorization "revelation": verified, built, null-tested, closed

Claim: `f73d92 = 2·11·149·4943` is not coincidence but the encoded instruction —
`11` = side of an 11×11 matrix, `121 = 11² = π(661)` prime positions of `DBBI‖FAED`
(`661 = 91+570`), `149` = VIC numeric-ciphertext length, `4943 = prime(661)`. Pipeline:
121 prime-position chars → 11×11 → row/col sums (matrixsumlist) → sums as indices into a
held text (lastwordsbeforearchichoice) → the extracted letters/words are the password.

**Every arithmetic claim is exactly true** (verified): `f73d92 = 16203154 = 2·11·149·4943`;
121 = 11²; the 121st prime is 661; the 661st prime is 4943; π(661) = 121; 661 = 91+570; and
the VIC numeric ciphertext **is** 149 digits. This is a genuinely tight-looking chain, tighter
than most, because it makes two independently checkable matches (149 = VIC length; 4943 =
prime(len DBBI+FAED)).

**But the operation it names is empty.** campaign_30 built the pipeline faithfully and
exhaustively over its natural parameter space:
- 121 prime-position chars of `DBBI‖FAED`, `a=1…i=9` (and `a=0…i=8`), 11×11 row-major and
  column-major, sums = row / col / row‖col / col‖row.
- **Letter-level** indexing (160 candidates) into held texts {Architect rewrite, VIC
  plaintext, URL, `DBBI‖FAED`, VIC ciphertext}, 1- and 0-based, reject/mod out-of-range.
- **Word-level** indexing (32 candidates) into the 332-word Architect speech, the VIC
  sentence, the checkerboard sentence, both digit maps.
Terminal gate: the 128-bit freeze oracle (both salts) + full-harness accept + address oracle.
**Result: 0 freeze hits, 0 harness hits, 0 address matches, and no readable output.** The
letter extracts are gibberish; the word extracts are salad ("otherwise it not has precision
not not and unexpected thus it…", with repeated "it it it" from duplicate sums).

**Null test on the factorization chain — it is a 1-in-11 coincidence.** Over 40,000 random
even 24-bit integers, against the puzzle's own quantity set
`{7,9,11,13,14,15,16,23,24,91,121,140,149,196,570,661}`:

| property | rate |
|---|---|
| a prime factor is a puzzle quantity | 0.31 |
| a prime factor's prime-index is a puzzle quantity | 0.23 |
| **both (the exact f73d92 chain)** | **0.094 (~1 in 11)** |

Small primes are common factors and the quantity set holds several small numbers, so a chain
this "tight" is an ordinary event — the same category as the π-digit chain closed at tick 21
(a 10% coincidence). The `149`-as-VIC-length and `4943 = prime(661)` matches are exactly what
a 1-in-11 process produces.

**Verdict.** The factorization is arithmetically real and unusually pretty, but it carries
~3.4 bits of evidence (chance level for this search) and the operation it supposedly encodes
produces nothing under a 2⁻¹²⁸ gate. Recorded as coincidence, not promoted to "the operation"
— consistent with the ledger's standing rule that a reproducible number is not a compelled one.
The matrixsumlist pipeline in its most-motivated instantiation (11×11 from `DBBI‖FAED` prime
positions) is closed; broader matrixsumlist readings on the 14×14 grid were already closed
(campaigns 12–19). The live gap is unchanged: an authenticated statement naming the operation,
or the lost S0 seed. Neither is in hand.

### Loop tick 33 (2026-09-26) — provenance page: name the operand for each slot (no AES)

Per the standing plan (no campaign until two slots hold source-forced values). Wrote
`unverified/endgame_provenance_page.md`: for each slot, the one primary sentence that names its
operand, or blank.

- **A** operand named (the 24 yellow/blue colour cells → `f73d92`, #1710 + #8446); **operation
  not named** — "primes" is SAL-scoped to `matrixsumlist`, and no sentence aims prime/zero/DEL
  at the colour value. A stays the number `f73d92`, not expanded (tick 32 closed the factorize
  route).
- **B** operand **not uniquely named** — #8446 gives the token, but no sentence says which
  matrix (14×14 grid vs 7×13 `DBBI` blocks) or which cells.
- **C** operand named (the Architect speech) and **boundary pinned from the bytes**: the phase-3.2
  plaintext contains no `door`/`choice`/`choose`/`left`; it ends
  `…goodluckneverthelessireallyhopeyouretheoneciaobellao`, so the choice boundary is the end of
  the text. C's whole byte-derived set (≤3): `ciaobellao`, `ireallyhopeyouretheone`,
  `goodluckneverthelessireallyhopeyouretheoneciaobellao`. The quintessential-delusion line
  (#3390) is **dropped** — not before this cut, and disclaimed by #3391.
- **D** is an output/checkpoint (#9599/#39224/#39237), not an operand.

**Retrieval inventory** (step 4): `HASHTHETEXT` is present (`decentraland.ipynb`);
`/followthewhiterabbit` was examined (tick 11, = the phase-1 verification page, no puzzle
content); S0 / the original S1–S4 script is absent from the archive **and** all git history
(tick 31) and is the uninvertible SHA256 preimage of head S1 — a genuine hole but not
retrievable, only re-derivable from the lost script. No retrievable hole remains.

**State.** Two slots still lack source-forced concrete values: C reaches a 3-string candidate
set, but A has no named operation, B's matrix is unnamed, D is an output. `combine` stays
illegal; no AES campaign. The next real move is a **named operand or operator** from a new
authenticated statement.

### Loop tick 34 (2026-09-26) — slot B pinned to the DBBI/FAED structure by soup position

**The soup position forces the matrix.** `matrixsumlist` is decoded from the a/b field at
offset 91:195, sandwiched between DBBI (0:91) and FAED (195:765). The creator names the method
next to its operands at every stage, so B's matrix is the **DBBI/FAED structure**, not the
genesis 14×14 grid. The provenance page's "which matrix?" ambiguity is resolved. Genesis row/col
sums (`610876654997879` / `8108108736759668`) are **deprecated** for slot B.

**Three source-forced B integer lists computed** (`campaign_31_matrixB.py`), from
`DBBI ‖ FAED[0:546] = 637 = 7×91` = seven 7×13 layers, digits a=1…i=9:
- **B-ew91** = element-wise sum of the 7 layers → 91 values, range 23–52 (the only index-sized list).
- **B-row7** = row sums of the element-wise 7×13 grid = `455 485 483 518 468 504 460`.
- **B-col13** = col sums = `268 241 285 276 254 266 241 245 277 266 255 245 254`.
`matrixsumlist` emits an integer list (indices for slot C), not a string to hash — so these are
frozen as lists, not fed to AES.

**The B→C extraction is empty (NEGATIVE).** Using B-ew91 as 1-based word indices into the
332-word Architect speech (the text slot C names) gives word-salad ("mathematical eventuality
been otherwise is a ananomaly been harmony what i have unable to…"); per-layer DBBI row-sums
("it of has thus a a beyond") and col-sums ("my what harmony from of been the unable to…")
likewise. No readable English emerged, so nothing advanced to the freeze/address oracle. (This
is the corrected matrix — the earlier campaign_30 used the 11×11 prime-position matrix, now
closed at tick 32; per-matrix 7×13 sum lists as passwords were closed at campaign 12.)

**FAED 24-tail vs colour frame (slot A↔B link, step 3).** `FAED[546:570] =
ibibbibdcbahaidhfahiihic` (24 chars) against the colour sequence `BBBBYBBBYYBBBBYBBYYBYYBY`:
blue-select → `ibibibdahaihfii` (15), yellow-select → `bcbdahihc` (9). Structurally the 24=24
alignment holds (as at ticks 13/17/19), but neither selection nor its digit list is readable or
recognisable. No source-grounded A→B link found.

**Slot C word-counts (step 4).** The C strings' word counts (1, 5, 7) as indices into the VIC
sentence / checkerboard sentence / URL give fragments ("in to this", "case crack the",
"raising extra of"), nothing readable.

**State.** B's matrix is now pinned and its candidate lists frozen — a real provenance advance.
But the pipeline B feeds (matrixsumlist → index → lastwordsbeforearchichoice) is empty of
readable output, and slot A still has no named operation. Per step 5 the combine stays illegal
and no AES campaign runs. The next real move remains a named operator on a named object.

### Loop tick 35 (2026-09-26) — VIC certified; last-words and FAED material closed; the terminal state

**Phase-3.2 VIC digit cipher fully certified.** The straddle-checkerboard with rowheads {1,4}
and alphabet `FUBCDORA.LETHINGKYMVPS.JQZXW` (28 cells = 26 letters + two dots) takes the
149-digit string to the 91-char sentence exactly. Three sub-tests settled its status:
- **alphabet source-forced** by the Phase-3.2 riddle itself (the page gives it), not fitted to a
  keyword — removes the "reverse-engineered to fit" objection;
- **{1,4} rowheads are named in the decoded plaintext** ("one for one, four for one") — the stage
  checks itself, but this does **not** inherit from `matrixsumlist`; the {1,4}↔layer-prime
  correspondence is an overlay under the a=0 map, not a consequence of VIC;
- **family check**: the AES envelopes carry no digit stream, so the board has nowhere to apply —
  VIC is local. `{1,4}` is not a reusable key on the 80-byte locks.

**The 31/73→42 and matrixsumlist→{1,4} results stay map-dependent.** They require a=0…i=8; the
house map o=0,a=1…i=9 gives 40/88 (composite) and layer primes at {5,7}. Null (tick verified):
both colour-sums prime ~1 in 18; layer primes exactly at {1,4} ~1 in 90; ~1 in 1600 together —
stronger than the f73d92 factorization (1 in 11) but not proof, and un-inherited from VIC. Held
at "strong structural reading," not promoted to key material.

**campaign_32 — the 48/96 last-word construction, closed.** Final 11/21 Architect words = exactly
48/96 chars (L96 splits 48/48, 2nd half == L48). Tested outside-the-box against miniA (ct 32),
salph (ct 80), P32T (ct 80): 61 explicit 32-byte privkey candidates (XOR/one-time-pad of the
strings against the cts and full blobs, sha/window key derivations, half-subtraction) → address
oracle; derived AES keys → decrypt + PKCS#7 + P32T freeze + 64-hex-in-plaintext → address;
password form (raw + sha256hex, EVP-MD5/SHA256). **0 address hits, 0 lock opens, 0 structure.**
Note: the 48/96 byte sizes include OpenSSL's 16-byte header, so miniA's message is ≤31 bytes —
the length match is partly to container overhead.

**campaign_33 — FAED-derived material, closed.** Layer sums `[331,360,369,421,418,441,396]`
(decimal concat, spaced, BE/LE 4-byte concat), the 24-char FAED tail and its reverse, the 24-cell
colour frame (raw/reversed/BY-swapped), `31/73/42` with five joiners, each alone and prefixed
with `yellowblueprimes`; raw / sha256hex / raw-key forms × EVP-MD5/SHA256 × miniA/salph/P32T.
28 strings, 62 password-forms, **0 hits.**

**Architecture, after the nulls.** Flat (decrypt = 32-byte key): every tested candidate null.
Two-stage (decrypt = seed → BIP32 child at a path → key): **untouched**, because the seed would
live inside an unopened lock — not testable without first opening a lock. The creator's plural
"the private keys belong to half and better half" fits two locks → two seeds → two keys → one
combining rule, but that is one decryption away from being testable.

**Terminal state (the honest frontier).** The password for the two real 80-byte locks is the only
thing between the current state and a forward step; every other channel — outer seeds, VIC reuse,
last-words, FAED material, colour factorization, salts, git history — is at the noise floor. The
missing input is not in the creator-authenticated corpus. This matches #66573/#66574 (2026-07-13,
"my close friends have the best chance … NOTE: that is a hint"): the last step is designed not to
be derivable from published material. That is a real terminal state, not a failure. The freeze and
address oracles remain as tooling for any password a fact-from-outside might supply.

### Regime change (2026-09-26) — corpus parked; one frozen gate for new primaries only

The lock-battery regime is over. Campaigns through 33, the 240 BIP32 derivations, VIC reuse and
the FAED/last-words grids are all null, and more forms of the same objects only produce PKCS#7
noise at the rates already measured. No more campaigns are run against the published corpus.

**What is established, and what is not.** No password for mini, P32T or Cosmic can be derived
from the published corpus through any tested channel. Flat decrypt-equals-key finds nothing on
that set. Two-stage HD cannot be tested until a seed exists, and none of the seeds in hand is it.
`#66573` ("my close friends have the best chance … NOTE: that is a hint") does **not** prove the
last step lies outside the corpus. This corrects tick 35's "designed not to be derivable". The solved text already contains readings of that line: "half
and better half", the couple who "need funds to live", the Matrix intimates. Those were tried as
seeds and passwords. So "close friends" means either those spent objects, or a social fact that
cannot be rebuilt from the page. Hashing more variants cannot tell which. VIC stays local.
`{1,4}` is named by "one for one, four for one", not by `matrixsumlist`. `31/73→42` depends on
the map. None of these is key material. The 2021 "another door" / "2nd way wasn't founded" line
is read as the same instruction: a path that is not a remix of SalPhaseIon.

**The gate** (`harness/gate.py`, frozen):
candidate → {raw, sha256hex} → EVP-{MD5, SHA256} aes-256-cbc → {miniA, miniAB, P32T, Cosmic}
→ strict PKCS#7 + printable/magic gate. In parallel, sha256(candidate) (and the candidate
itself, if it is 64 hex) → uncompressed P2PKH compared with `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.
Each intake gets 16 decrypts. No sliding windows, no substrings picked by the gate, no 2ⁿ
subset XOR.

Admissible input, one candidate per intake file, refused otherwise:
- `jrk_sentence`: a new Jrk/@SoWut message with id, date, author and the full verbatim text;
- `gsmg_page`: a new gsmg.io page with url, fetch time and the saved body (the 9-byte
  `Hello :-)` 404 is refused);
- `uttered_password`: a password a person in that circle actually said, with speaker, date and
  where it was said. Inferred passwords are refused.

Refused as spent before any decrypt: an exact string (raw or sha256hex) already in
`attempts/*.jsonl`; any string whose normalized a-z0-9 form occurs in LEDGER.md, `materials/`,
`materials/primary/`, `prior-sessions/`, `unverified/`, or among the literal candidates in
`harness/campaign_*.py` and `attempts/*.txt` (so campaigns 32/33, which wrote no JSONL, count); and anything already run through the gate
(`attempts/gate_intake.jsonl`). `gate.py --selftest` checks the three solved blobs, the address
known-answer vectors, the spent-refusal cases (half/better half, causality, the 3.2 password,
matrixsumlist), the provenance refusals, the 404 refusal, and confirms that the frozen decrypt
path reproduces phase 3.2.

**Standing state.** Slot A stays unfilled and slot C stays blank until one of the three primaries
arrives. Sandwich-B and `a=0` are not promoted to operators. If no primary appears, stop: the
tooling waits, and the only proof that counts is a spend from the prize address.

### Intake 1 (2026-09-26): uploaded Wayback, primary and drive material digested; nine web units gated, all null

**What arrived.** Three user archives:
- **Wayback:** 545 gsmg.io captures, 450 unique bodies after gzip/brotli/zstd decoding.
  Indexed in `materials/wayback/`.
- **Primary archive:** 65 files. Every one is already in the repo or byte-identical to a Wayback
  capture; the only extra is the raw binary of the 2023-02-23 hint, whose decoded form is here.
- **Drive export:** 9 files, filed under `unverified/drive-2026-05/`.

**What was new, and what it was worth.**
- **Tick 11 was wrong about the finale page, and right about its keys.** `root_2026-08-19` is a
  GSMG shutdown page: "2017 — 2026", "The lights are off.", "Nine years of chaos ended. One
  mystery remains.", with "Follow the white rabbit" linking to `/puzzle`. It types two Matrix
  terminal lines, then renders a hard-coded 14×14 grid under "SYSTEM FAILURE". That grid is
  **exactly the phase-1 grid**, with blue set to 1 and yellow to 0, and its spiral read is
  `gsmg.io/theseedisplanted`. So there is text, but no new operand.
- **The domain lapsed.** "The sites are down" drew "The puzzle is still valid!" (#63957,
  2026-05-28). From 2026-07-07 to at least 2026-08-10 gsmg.io was a parked domain listed for
  sale (abovedomains `forsale.min.js`, FingerprintJS `tr_uuid` redirects). The finale appeared
  on 2026-08-19. **Anything served on gsmg.io after 2026-07-07 has unverified authorship.** Any
  future `gsmg_page` intake from after that date carries the caveat.
- **A comment was added to the phase-2 page** between 2022-12-23 and 2026-04-05:
  `<!-- You made it to the next step! Good luck little bunny hunter ;) -->`. It is the only
  HTML comment on either live puzzle page. SalPhaseIon changed only in whitespace (2024-11)
  and a Cloudflare beacon (2025-10).
- **The SPA carries one puzzle string.** Across all 11 app.js versions, the `/puzzle` route shows
  `GSMG MEGANIGMA || 5 BTC` above the white-rabbit image. `/yummy` is the Cookies Policy. The
  legal PDFs are boilerplate for Epipremnum Aureum LLC (Saint Kitts–Nevis).
- **Every other path is the SPA shell**, including the guessed ones (`/merovingian`,
  `/final_stage`, hope-line spellings), 10 of the 12 hex paths, and a hex-encoded `Salted__`
  blob with a salt that appears in no known material. Shell diffs are infrastructure only.
  Of the other two hex paths, `/89727c…` is the SalPhaseIon page. `/4f7a1e4e…`, requested
  on 2026-07-08 while the domain was parked, is `sha256(cosmic_1327b_decrypted.bin)` from the
  drive export. Someone tried the sha256 → URL convention on a noise decryption
  while the domain was parked.
- **Drive export verdicts.** Four files are copies of known blobs. The two 1327-byte "Cosmic
  decryptions" are 1-byte-pad noise (entropy 7.8+, no structure). `ca158_hidden_blob` starts
  `Salted__`, but its 1153-byte body is not a multiple of 16, so it cannot be an openssl
  AES-CBC envelope; its source file is not in the export. `chain2`/`chain4` are pad-1
  decryptions of its first 1152 bytes.
- **The 2026-01-01 new-year hint is already in the transcript** (#53342): 'Happy new year! Make
  the best of everything. Oh, and here's a "tiny hint" <3.' The quoted "tiny hint" echoes #881,
  the 2019 promise of a "tiny hint" at the start of 2020. The five preceding messages of one to
  five dots are logged as NOISE. As Morse they read E, I, S, H, 5, the dots-only ladder. That
  is recorded as a reading, not promoted to an operand.

**The gate run.** `intake/2026-09-26-web/PREREG.md` was committed and pushed before anything
ran. It covers every solver-facing text unit of the three new sources, whole and verbatim,
nine intakes: the phase-2 comment, `GSMG MEGANIGMA || 5 BTC`, "The lights are off.", "Nine
years of chaos ended. One mystery remains.", "2017 — 2026", "WARNING: carrier anomaly",
"Trace program: running", "SYSTEM FAILURE", and the rain-glyph string. All nine were admitted.
**144 decrypts, 0 with valid PKCS#7 padding at all (about 0.6 expected by chance), 0 prize
address.** Each is logged in `attempts/gate_intake.jsonl` and is now spent.

**Stop rule applied.** The 2026 web material is closed: no variants, no concatenations, and the
timing constants (1441, 2442 ms …) are not promoted. Nothing in the three archives is a new Jrk
sentence or an uttered password. Standing state is unchanged: A unfilled, C blank, tooling
waiting.

### Loop tick 36 (2026-09-26): the checksum machine, cold-verified, classified and frozen

**Verified.** `harness/verify_checksum_machine.py` recomputes every claim from primary files
(soup, `phase3-assets/phase3.2.txt`, the phase-0 grid JSON). No AES, no gate. **26 of 26 checks
pass**, including each uniqueness scan.

The tape, as it now reads:

```text
soup[0:91]     DBBI (91, a–i)     layer 1 of 7: a=0 total 331 (prime, π=67)
soup[91:195]   bin1 (104, a/b)    48 a / 56 b; a=0,b=1 packed MSB-first = "matrixsumlist";
                                  bit[31]=0, bit[73]=1 (Yellow=0 / Blue=1 polarity), 31+73=104
soup[195:765]  FAED (570, a–i)    [0:546] = layers 2–7: 360 369 421 418 441 396 (421 prime, π=82)
                                  [546:570] = tail; phase-0 frame BBBBYBBBYYBBBBYBBYYBYYBY gives
                                  Yellow=31 / Blue=73 under a=0
DBBI‖FAED = 661 symbols; 4943 = p_661; 0xF73D92 = 2·11·149·4943
```

- **Colour window:** of 547 windows of 24 on FAED, only offset 546 gives 31/73 under a=0. The
  house map gives no 31/73 window anywhere; the tail reads 40/88 there.
- **Layer totals:** of the 25 alignments of a 637-block on the 661 tape, only offset 0 has
  primes at positions {1,4}, values {331, 421} and rank-sum 67+82 = 149.
- **VIC split:** the 149 VIC digits decode to the 91-letter sentence on the proven board
  (91 tokens). Letter 40 ends exactly at digit 67, so 67 | 82 decode separately to
  `INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYS` | `BELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE`.
  That is the sentence boundary.
- **The one 42:** token `42` occurs once in the tokenization (it is also the only raw `42`
  substring), at digit 47, and it is the `P` of PRIVATEKEYS. Board: 42→P, 15→I, 10→`.`, 43→S.
- **ENTER mask:** the 40 bits of `enter` over the first 40 letters (A=0…Z=25) sum to 191 where
  the bit is 1 (prime, π=43, board code `S`, the last letter of PRIVATEKEYS) and 233 where it
  is 0 (prime, π=51 = the 51 remaining letters). The gap is 42. Of 52 windows of 40, only
  offset 0 gives a prime pair with gap 42.
- **Lengths:** π(11)=5=|enter|, π(149)=35=|shabefourfirsthintisyourlastcommand|.

**Precision notes, from the check.**
1. **π was never uttered as a function.** In 510 creator-log rows, the prime-counting function
   π(n) and "rank" never appear. The only "pi" is #32671 (2024-11-29), "You only need the last
   number of pi…", which is banter about the constant and was closed as key/IV material at
   tick 22.
2. **Two conventions carry the machine.** 31/73 exists only under a=0, which is not the house
   map. The ENTER pair exists only with MSB-first bits: LSB-first gives 218/206, both even.
   MSB-first is at least the soup's own bin1 packing, so that one is internally consistent.
3. **Correction to the campaign-32 remark.** Its 64-hex regex ran on AES decrypts, never on an
   XOR output. It was dead only on miniA's 32-byte decrypt and live, with low power, on the
   80-byte locks and Cosmic. The code that really was dead is the XOR scan's
   WIF/`xprv`/`1GSMG` prefix loop, whose body is `pass`, so XOR outputs were checked only for
   `Salted__` and ≥90% printable. The script also reads `/tmp/arch_words.txt`, which is not in
   the repo, so campaign 32 cannot be reproduced as committed. Its null stands and is not
   re-run.

**What it is.** A closed arithmetic commentary on the already-decoded Phase-3.2 and SalPhaseIon
layout. Every output lands on a length or a cut already in hand: 149, PRIVATEKEYS, HALF AND
BETTER HALF, `enter`, 661, matrixsumlist.

**What it does not do.** It does not name a creator-written operation for slot A, does not fill
C from a new primary page, does not open mini, P32T or Cosmic, and does not produce a 32-byte
scalar for `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe`.

**Frozen as not key material.**
- `4943`: reading it as p_661 is the best reading of that marker so far, but it is still the
  frozen Genesis object. It is not hashed, not used as an offset and not put in the gate.
- The length zoo, such as π(42)=13=|matrixsumlist|, π(31)=11=|thepassword| and
  π(15)=6=|YOUWON|, is look-elsewhere and stays off the key list.
- `42 15 10 → PI.` (73−31, 82−67, π(73)−π(31) on the board) is a wink, not a password.

**The continuation rule, frozen.** If the machine is continued at all, it takes the **next
source-named** binary mask × an equal-length named text, demands another prime-pair / π
checkpoint, **then stops. No AES.** Masks already spent: the Phase-0 24-colour frame and the
`enter` 40 bits. A next mask must be as named as those two (`shabefour…`, `hash_the_text`, a
creator bit-string), not one cut because it is the right length.

**Gate: empty.** Standing state unchanged: A unfilled, C blank. This tick improved the ledger's
description of the tape. It did not solve the puzzle.

**Tick 36 addendum: base rates for the "π(x) is the operator" reading.** The same facts were
re-presented as evidence that the prime-counting function is the missing operator.
`harness/checksum_machine_baserates.py` measures what each fact is worth.
- **Uniqueness is mostly automatic.** Of 547 FAED colour windows, 344 already have a (Y,B) pair
  that no other window shares; 31/73 was read off offset 546, so its uniqueness is expected.
  A prime pair 42 apart is **not** unique on FAED: offset 110 gives 29/71. Of the 25 tape
  alignments, 15 have a prime-position pattern that no other alignment shares, and {1,4} is
  simply the offset-0 pattern.
- **The 67 | 82 cut.** 22 of 148 digit cuts land on both a token boundary and a word
  boundary, so landing on one is a **15%** event. The notable part is π(331)+π(421) = 149,
  the VIC length, a chain of the kind tick 32 measured at about 1 in 11.
- **The length zoo is nearly free.** Newly checked: π(104)=27=|verylaststepisatruegiveaway|,
  π(10)=4=|HALF|, π(21)=8=|promised|, π(4943)=661. Against 24 named tokens, π(n) hits a named
  length for **78% of n ≤ 50** and 35% of n ≤ 150.
- **What survives: ENTER.** A random 40-bit mask over a random 40-letter window gives a prime
  pair exactly 42 apart about **1 in 1,400** times. That the natural mask on the natural
  prefix repeats the 42 is the one genuinely unlikely item. It still depends on MSB-first
  bits and A=0, and what it points at is the solved sentence (PRIVATEKEYS, the 51-letter
  remainder), not an operand.

**Verdict unchanged.** Grant π(x) as the creator's device and it is still a device for
checksumming lengths and cuts of decoded text. It emits no string, key or scalar that any lock
could take, and no source-named next mask exists to feed it. The frozen continuation rule
stands; the gate stays empty.
