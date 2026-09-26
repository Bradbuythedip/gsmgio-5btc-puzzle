#!/usr/bin/env python3
"""Campaign 53: the one date the creator gives away, Neo's passport expiry (pre-registered).

#8048 (2021-12-31) @SoWut: "The only date I give away is the expiry date of neo's passport."
  (in reply to "...i also want to ask questions like, how old are you")
#8516 (2023-05-02) @SoWut: "Still remarkable that scene. Especially the expiration date of his passport."
The Matrix (1999): Thomas A. Anderson's passport expires 11 Sep 2001, printed "11 Sep/Sep 01".

Pre-registered in intake/2026-09-26-passport/PREREG.md, committed before this run. CANDIDATES is
that list verbatim; nothing is added after the fact. No form of the date had been tried in any
campaign, the gate, or the ledger. It is a creator-named object, not a verbatim string, so it runs
here on the gate's frozen path (as campaign 52 did), not as a gate intake.

Per candidate: the frozen gate path ({raw, sha256hex} x EVP-{MD5,SHA256} x {miniA, miniAB, P32T,
Cosmic} = 16 decrypts, strict PKCS#7 + printable/magic), the P32T last-block freeze, campaign 51's
padding-independent scan of the same decrypts, and addr_check's fixed encodings vs prize / 17ucy1
/ 1NULY7.

  python3 campaign_53_passport_date.py
"""
import json, os, sys, time
from datetime import datetime, timezone
import gate, aes_try, btc_addr, p32t_freeze, addr_check
from campaign_51_padding_independent import scan

OUT = os.path.join(gate.NEO, "attempts", "campaign_53_passport_date.jsonl")

CANDIDATES = [
    # as printed on the passport, and its normalizations
    "11 Sep/Sep 01", "11 SEP/SEP 01", "11sep/sep01", "11sepsep01", "11SEPSEP01",
    # day-month-year, text
    "11 Sep 01", "11sep01", "11SEP01", "11 Sep 2001", "11sep2001", "11SEP2001",
    "11 September 2001", "11september2001", "11-Sep-2001",
    # month-day-year, text
    "September 11, 2001", "september112001", "September 11 2001", "sep112001", "sept112001", "Sep 11 2001",
    # numeric day-month-year
    "11092001", "11-09-2001", "11/09/2001", "11.09.2001", "110901", "11-09-01", "11/09/01", "11.09.01",
    # numeric month-day-year
    "09112001", "09/11/2001", "09-11-2001", "9/11/2001", "9-11-2001", "091101", "09/11/01", "9/11/01",
    # year-month-day and machine forms: MRZ YYMMDD, MRZ + ICAO check digit, unix time 00:00 UTC
    "20010911", "2001-09-11", "2001/09/11", "2001.09.11", "010911", "0109110", "1000166400",
    # the iconic short forms
    "9/11", "911", "0911", "1109", "september11", "11september", "nineeleven", "nine eleven",
]

def mrz_check(digits):
    """ICAO 9303 check digit: weights 7, 3, 1 repeating, sum mod 10."""
    return str(sum(int(d) * (7, 3, 1)[i % 3] for i, d in enumerate(digits)) % 10)

def main():
    assert len(CANDIDATES) == 51 and len(set(CANDIDATES)) == 51, "list differs from PREREG.md"
    assert "0109110" == "010911" + mrz_check("010911")
    assert int(datetime(2001, 9, 11, tzinfo=timezone.utc).timestamp()) == 1000166400
    assert (aes_try.self_test() and btc_addr.self_test() and p32t_freeze.self_test()
            and addr_check.self_test()), "self-test failed"
    targets = aes_try.load_targets(); t32 = targets["inner96"]
    tot = pads = hits = 0
    with open(OUT, "w") as f:   # truncated first, so this run's own log cannot mark candidates spent
        tried, (corpus, tokens), intake = gate.load_tried(), gate.load_corpus(), gate.load_intake_log()
        corpus = corpus.replace(gate.norm(open(__file__).read()), "|")   # nor can this file's literals
        addr_matches = addr_check.check([(c, c.encode()) for c in CANDIDATES])
        for c in CANDIDATES:
            spent = gate.spent_reason(c, tried, corpus, tokens, intake)
            dec = gate.run_decrypts(c, targets)
            frz, pind = [], []
            for form in gate.FORMS:
                pw = (c if form == "raw" else gate.sha256hex(c)).encode()
                for kdf in gate.KDFS:
                    md, kl = aes_try.KDFS[kdf]
                    key, _ = aes_try.evp_bytes_to_key(pw, t32["salt"], md, kl)
                    if p32t_freeze.primary_ok(key) or p32t_freeze.secondary_ok(key):
                        frz.append((form, kdf))
                    for tname in gate.TARGETS:
                        t = targets[tname]
                        k, iv = aes_try.evp_bytes_to_key(pw, t["salt"], md, kl)
                        for where, (which, addr) in scan(aes_try.decrypt(t["ct"], k, iv)):
                            pind.append((form, kdf, tname, where, which, addr))
            am = [m for m in addr_matches if m[0] == c]
            near = [r for r in dec if r["pad"]]
            h = any(r["hit"] for r in dec) or bool(frz) or bool(pind) or bool(am)
            tot += len(dec); pads += len(near); hits += h
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "pw": c,
                                "spent_before": spent, "decrypts": dec, "freeze": frz,
                                "padding_independent": pind, "addr_matches": am, "HIT": h}) + "\n")
            print(f"{c!r:22s} pad={len(near)} freeze={frz or '-'} pind={len(pind)} addr={len(am)} "
                  f"HIT={h}  [{spent or 'new'}]")
    print(f"\ncandidates={len(CANDIDATES)} decrypts={tot} pkcs7_any={pads} hits={hits}")
    print("*** HIT ***" if hits else "null. The passport expiry date opens no lock and derives no "
          "target address; the direction is closed per the pre-registration.")
    return 10 if hits else 0

if __name__ == "__main__":
    sys.exit(main())
