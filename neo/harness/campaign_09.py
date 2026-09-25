#!/usr/bin/env python3
"""Campaign 09: broad dictionary + numeric blitz under the pinned convention.

- 370k English words (dwyl words_alpha) and 10k common passwords: raw and sha256hex,
  s2 KDF, against miniA/miniAB/inner96/cosmic.
- integers 0..999999 as strings, same treatment, miniA/miniAB/inner96 only.
Logs only pad-valid results (as ever); the tried-space is reproducible from this file.
"""
import hashlib, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness

SCRATCH = "/tmp/claude-0/-home-user-gsmgio-5btc-puzzle/bbd23b02-cb65-5083-b385-f9851132669a/scratchpad"
TARGETS = ["miniA", "miniAB", "inner96", "cosmic"]

def main():
    h = Harness("campaign_09")
    sha = lambda s: hashlib.sha256(s.encode()).hexdigest()

    for path, tag in ((os.path.join(SCRATCH, "words_alpha.txt"), "dict"),
                      (os.path.join(SCRATCH, "10k.txt"), "10k")):
        n = 0
        for line in open(path, encoding="latin1"):
            w = line.strip()
            if not w:
                continue
            h.try_pw(w, tag, targets=TARGETS, kdfs=["s2"])
            h.try_pw(sha(w), tag + "|sha", targets=TARGETS, kdfs=["s2"])
            n += 1
            if n % 100000 == 0:
                print(tag, n, "words done,", h.n, "trials", flush=True)
        print(tag, "total", n)

    for i in range(1000000):
        s = str(i)
        h.try_pw(s, "num", targets=["miniA", "miniAB", "inner96"], kdfs=["s2"])
        h.try_pw(sha(s), "num|sha", targets=["miniA", "miniAB", "inner96"], kdfs=["s2"])
        if i % 200000 == 0:
            print("num", i, flush=True)

    h.finish("campaign_09")

if __name__ == "__main__":
    main()
