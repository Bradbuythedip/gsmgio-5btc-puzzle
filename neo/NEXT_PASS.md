# NEXT_PASS — grave-detail state and the next pass (2026-09-26)

A four-agent audit (MITM/EC, AES-lock acceptance, soup→string operators, primary provenance) plus
three new committed campaigns (50/51/52). This file is the map for the next pass: what is proven
dead, what the audit *closed*, and the few levers that remain. The accept predicate is unchanged:
**the prize `1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe` is unspent (~1.25 BTC). Nothing is solved until it spends.**

The two live targets are the **SalPhaseIon short lock** (miniA‖miniB, salt `3ab585348552415d`, 80-byte ct)
and the **Phase-3.2 trailing lock P32T** (inner96, salt `b45a5e3d827593ca`, 80-byte ct). **Cosmic**
(salt `2d3f6fe06dc950e6`, 1328-byte ct) is a third, separate object. All three ciphertexts are now
byte-verified across ≥3 independent sources (see §3), and byte-pinned by envelope sha256:

| object | envelope | sha256 (96/1344 B) | last ct block |
|---|---|---|---|
| SalPhaseIon short (miniA‖miniB) | 96 B | `9e2831e1b34b5f34796df47ccaf6530d48d371c61a6bff84d60db1064fa7a258` | `ef756397ea74234a97a95f01ae37f8c9` |
| P32T / inner96 | 96 B | `291dfd6f3e759ec2e272b35a00c24907da70c3e7a9291b4c13605c7b0b4f3de9` | `5334de08884878aaed7c99d0b4340bf8` |
| Cosmic | 1344 B | `b18950551a4dd0cb8a9378f0906ba18c03a15f0ee83eb98c6bc90165c5f79805` | `5bbf983669ed922eb12dff1dcc3f6fc6` |

---

## 1. Do-not-repeat inventory (ticks 1–88)

| class | status | where |
|---|---|---|
| Password sweeps on the published corpus (VIC, DBBI/FAED, last-words, matrixsumlist, seven-token concats, Matrix/Fresco/Venus vocab, "42", yinyang/yellowblueprimes labels) | **null**, 100k+ decrypts | ticks 1–35, 48–49, 74, 80 |
| KDF space — EVP_BytesToKey {MD5,SHA1,SHA256}×{32,16}, raw-key, **AND PBKDF2-HMAC-{sha256,sha1,md5}×6 iters** (validated vs OpenSSL 3.0.13) | **null**, controls pass | 81 |
| π-as-digits (640k decrypts) and π-as-prime-counting | forced / length-zoo, no key | 22, 73 |
| Graph/structural numerology — K₁₄, 196=91+14+91, f73d92, checksum machine | forced-by-construction / null | 32, 36, 67–68, 76 |
| EC vs prize key — MITM a±b/a·b (163k pool), affine-nonce (6 sigs), Issue-#79 combos, BSGS-on-prize | **null** / declined | 37, 71–72, 78, 50 |
| **MITM with the *corrected* pool** (S1–S4 seeds, canonical answers, salts, layer sums added) | **null** | 83 / `campaign_50` |
| **Accept-rule false-negative** (padding-independent full-plaintext address/key oracle, bypasses PKCS#7 gate) | **null**, 464 decrypts | 83 / `campaign_51` |
| **Natural last-words phrases decrypted bare** (were gate-refused, never decrypted) | **null**, 224 decrypts | 84 / `campaign_52` |
| Soup→string operators (DBBI⊖VIC=YOUWON is terminal; FAED carries no planted string; both a/b blocks consumed) | exhausted | 8–11, 15, 20, 34–35, 84 |
| On-chain trail — locktimes 629998 (signed) & 840003, "neighbors half and double" = points, Good-job-Neo brainwallets, Half/Better = solver dust (NONE creator-funded); **receipt topology**: the halves transact (2020/2024 splits, the 2020 one signed over the `3GSMG24T` "Halving" memo), never co-sign; `17ucy1` receive-only | **null** | 37–38, 52–53, 59, 63, 77, 79, 88 |
| Community "solutions" — jackdevs66 XOR-of-seven = 7.87-bit noise / 1-byte pad; Issue #79 keys from that noise; Murray not Genesis; Issue #108 "two typos" a non-issue | falsified | 7, 75, 78, 82, 85 |
| **Dates** — Satoshi's P2P birth date / EO 6102 / gold (no creator anchor → unlicensed); **Neo's passport expiry 11 Sep 2001** (the creator's only named date, #8048/#8516), 51 pre-registered forms | **null**, 816 decrypts | 87 / `campaign_53` |

## 2. What the audit found and CLOSED (three escape-hatches)

1. **MITM ran the right method on the wrong pool → fixed, null.** Tick 37's point-collision MITM was
   correct but its pool lowercased and 4-word-capped everything, dropping the S1–S4 seed scalars,
   most canonical answers, `YOUWON`, `yinyang`, the layer-sum concatenations, and the three salts.
   `campaign_50` re-ran with all added: **no `half ± better` / `half·better` relation to Q.** Also
   newly closed: `17ucy1…` is not `Q/2`, `2Q`, or `Q±G` — it is an independent key with no public
   pubkey (never spent) and therefore no MITM surface.
2. **The accept rule could silently reject the true password → tested, null.** `check_pt` hard-fails
   on invalid PKCS#7 *before* any printability/address test, and the address oracle sits behind that
   gate; in CBC a bad final block (or a −nopad raw key) breaks only the last plaintext block. A right
   password could look identical to null. `campaign_51` bypasses the pad gate (scans the full
   plaintext for a 64-hex→prize address, tests `pt[:32]`/`pt[32:64]` as raw keys, tail-robust
   printability): **0 hits in 464 decrypts.** The gate was not hiding a known-candidate answer.
3. **Ciphertext-transcription risk (tick 81) → closed in-repo, verified.** Two independent wayback
   captures (`materials/wayback/pages/salphaseion_2024-11-23.html`, `…2025-10-31.html`) carry the soup
   byte-identical to the primary (sha256 `d39d10b1…`; it contains both mini-lock base64 runs) and the
   Cosmic block decoding byte-identical to the 1344-byte envelope (sha256 `b1895055…`). Three sources
   agree; every EVP/PBKDF2 null is now robust to transcription as well as KDF.

## 3. Meet-in-the-middle — the honest verdict (your focus)

The MITM *method* in `mitm_halves.py` is correct and complete for group operations: build the table
`{aG: a}` over the pool, then for each `b` test `Q−bG` (k=a+b), `Q+bG` (k=a−b), `b⁻¹Q` (k=a·b). It is
**O(pool)**, not O(pool²) — adding scalars is nearly free. XOR and concatenation are not group ops and
cannot be MITM'd (must enumerate). What we now know:

- **The pool was the gap, and it is closed** (§2.1): the corrected pool is null.
- **`17ucy1…` has no MITM surface** — no public pubkey. The better half is reachable only by opening
  its AES lock or a *small direct* candidate set, never by pooled EC combination (O(pool²) address
  derivations ≈ 2.6×10¹⁰, infeasible, and no point test without its pubkey).
- **The Tick-47 model makes MITM a side-check, not the main line**: two independent keys behind two
  AES locks with no arithmetic relation. If that holds, no pool or rule recovers them by EC; the
  blocker is the AES password (non-EC). The 80-byte lock plaintexts cannot seed a pool (chicken-egg).
- **The one EC avenue declined-by-policy, not closed-by-math: BSGS around a seed center.**
  `bsgs_harness.py` is validated to 2³⁸. Feasible to ~2⁴⁴–2⁴⁸ on CPU. The one center with support:
  `prize = C_i(S_j) + small vanity offset` (the creator demonstrably makes vanity points — the 2021
  outputs are literally Q±G, Q/2, 2Q). It needs only the seeds S1–S4 (in-repo) + Q (now public), not
  the lost S0. This is the single un-run EC test; low prior but bounded (48 runs × ~minutes each).

## 4. Remaining levers (ranked) — most need your unblocked machine

1. **The Telegram group JSON export** (highest). Resolves ~6 threads at once: the #60312 "Bingo"
   threading (is the *Looking Forward* reading creator-confirmed or banter), the truncated tails of
   #66568 ("…the actual answer…"), #66592, #32579, #8569's three questions, and #60307's parent.
   It is the only source that could surface a creator line naming an operation on an 80-byte blob.
2. **A correctly-targeted human ask** — NOT the 2020 checkpoint recipients (worthless: those are
   `sha256(public-answer)` brainwallets, tick 62). Ask the **lead solvers** the creator himself said
   got "really really far" / past "the hardest part" (#4694, #6541, #8795/#8796, #9627; VrsN's team):
   what SalPhaseIon *intermediate* they reached past phase 3.2. An uttered intermediate is
   gate-admissible (`uttered_password`).
3. **BSGS-from-seed-center** (§3) — the one EC test I can run here; say the word.
4. **Extract + diff the 2023-11-27 SalPhaseIon capture** (wayback ts `20231127181947`) to formally
   retire the last 1% of the transcription item. Low effort, low value (2024/2025 captures already match).
5. **Verify `1NULY7…` history** on a block explorer (USER-grade oracle target; egress-blocked here). Same
   trip, topology only (tick 88): parents of the 2024 split's inputs `81d35929…:0`/`f28b0b68…:0` (a 2024
   "Halving" memo?), the inputs of `3GSMG24T`'s funder `547246e9…` (→ `1EtbTv…`?), raw hex of `a82052a2…`.

## 5. The crux (why nothing derivable has worked)

The creator evidence points to **derivable-but-unrecognized with a social recognition-shortcut**, not
a pure out-of-corpus secret: "you have all the info" (#9607), "internet not required" (#16624),
"it's in front of your eyes… you're not seeing it" / "very last step is a true giveaway" (#8446), "1
microstep further… solved the same day" (#32579) — against "my close friends have the best chance…
but they don't have the skills some of you do. NOTE: that is a hint" (#66573/#66574). A live fork the
ledger has not carried forward: if #66573's "it" is the **secret/payload** (#66592 "a secret I wanted
to share"; #66593 "the '5' btc was never the actual prize, only a tiny fraction"), then the **BTC key
may still be corpus-derivable** and only its *meaning* is social. The Telegram export is what
distinguishes these.

**Bottom line for the next pass:** no compute on the published corpus is expected to open the locks —
the KDF, accept-rule, transcription, MITM-pool, and soup-operator escape-hatches are now all closed.
The productive moves are external (export, lead-solver ask) plus the one bounded EC check
(BSGS-from-seed-center). Watch `1GSMG1…`; feed any creator-named string or uttered intermediate through
`gate.py`.
