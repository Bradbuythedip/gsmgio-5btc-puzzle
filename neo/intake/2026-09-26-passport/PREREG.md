# Pre-registration: the one date the creator gives away — Neo's passport expiry (2026-09-26), before the run

**Why this exists.** User-relayed question: does any authenticated puzzle object point to Satoshi's
self-reported P2P-Foundation birth date (5 Apr 1975) or to EO 6102 / gold? The census (tick 87) answers
no. The same census surfaced the only creator line about which dates he gives:

- **#8048, 2021-12-31, @SoWut:** "The only date I give away is the expiry date of neo's passport."
  (in reply to @insideyourpinealgland: "…i also want to ask questions like, how old are you")
- **#8516, 2023-05-02, @SoWut:** "Still remarkable that scene. Especially the expiration date of his passport 😁."

**Referent.** *The Matrix* (1999), first Agent-Smith interrogation (~18:22): Thomas A. Anderson's
passport expires **11 September 2001**, printed bottom-right as "11 Sep/Sep 01" (Snopes and Yahoo
fact checks; the creator-log annotation independently gives 11 Sep 2001).

**Status before the run.** No form of this date occurs in `attempts/*.jsonl`, the gate intake log,
the ledger, or any campaign source (checked: 0 hits for passport / 20010911 / 11092001 / 11sep…).

**Prior: low.** #8048 deflects a personal question ("how old are you") and is filed LORE, not HINT.
It is run only because (i) it is the single date the creator names, twice, 16 months apart; (ii) it
has never been tested; (iii) the test is bounded. It is a creator-named *object*, not a verbatim
string, so it is not a gate intake; it runs as a campaign on the gate's frozen path, as campaign 52 did.

## Candidates (fixed: 51 strings, in this order)

| family | strings |
|---|---|
| as printed + normalizations (5) | `11 Sep/Sep 01` `11 SEP/SEP 01` `11sep/sep01` `11sepsep01` `11SEPSEP01` |
| day-month-year, text (9) | `11 Sep 01` `11sep01` `11SEP01` `11 Sep 2001` `11sep2001` `11SEP2001` `11 September 2001` `11september2001` `11-Sep-2001` |
| month-day-year, text (6) | `September 11, 2001` `september112001` `September 11 2001` `sep112001` `sept112001` `Sep 11 2001` |
| numeric DMY (8) | `11092001` `11-09-2001` `11/09/2001` `11.09.2001` `110901` `11-09-01` `11/09/01` `11.09.01` |
| numeric MDY (8) | `09112001` `09/11/2001` `09-11-2001` `9/11/2001` `9-11-2001` `091101` `09/11/01` `9/11/01` |
| YMD + machine forms (7) | `20010911` `2001-09-11` `2001/09/11` `2001.09.11` `010911` (MRZ YYMMDD) `0109110` (MRZ + ICAO 7-3-1 check digit) `1000166400` (unix, 00:00 UTC) |
| iconic short forms (8) | `9/11` `911` `0911` `1109` `september11` `11september` `nineeleven` `nine eleven` |

## Protocol (frozen path)

Per candidate: {raw, sha256hex} × EVP_BytesToKey-{MD5, SHA256} aes-256-cbc × {miniA, miniAB, P32T,
Cosmic} = 16 decrypts, strict PKCS#7 + printable/magic (`aes_try.check_pt` via `gate.run_decrypts`);
the P32T last-block freeze (`p32t_freeze` primary/secondary); the padding-independent scan of
campaign 51 on the same 16 decrypts; `addr_check`'s fixed encodings (sha256, sha256d, rawpad, bitrev,
byterev; compressed + uncompressed) vs prize `1GSMG1…`, `17ucy1…`, `1NULY7…`.

## Decision rule (fixed before the run)

- **HIT** = any strict-pad hit with printable/magic, any P32T freeze pass, any padding-independent
  address/key hit, or any address match. Report, stop, widen nothing.
- **Null** = the passport-date direction is closed. No other passport fields (issue date, birth
  date, number), no other film dates, no translations, no further format variants. The Satoshi
  birth date, 6102/1933/1975 and the biblical-calendar mapping stay unlicensed (no creator anchor).
