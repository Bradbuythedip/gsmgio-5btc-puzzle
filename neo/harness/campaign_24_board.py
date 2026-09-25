#!/usr/bin/env python3
"""Tick 1b (preregistered, narrow): 2x14 board coordinates vs P32T ONLY.

Two fixed boards, reported separately, never blended:
  A = FUBCDORA.LETHINGKYMVPS.JQZXW
  B = fubcdora/lethingkymvpszjqwx.
Layout: 2 rows x 14 cols. row0 = chars 0..13, row1 = chars 14..27.

Protocol frozen: candidate -> {raw, sha256hex} x EVP-{md5,sha256} x P32T(inner96) only.
Strict gate (pad>=4 or magic or printable). Cosmic excluded on purpose.
"""
import os, sys, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness

BOARDS = {"A": "FUBCDORA.LETHINGKYMVPS.JQZXW",
          "B": "fubcdora/lethingkymvpszjqwx."}

def coords(board, word):
    """(row,col) for each letter of word, word order; letters matched case-insensitively."""
    up = board.upper()
    out = []
    for ch in word.upper():
        i = up.find(ch)
        if i < 0:
            return None
        out.append((i // 14, i % 14))
    return out

def serials(cs):
    """All preregistered serializations of a coordinate list."""
    s = {}
    s["col0"] = "".join(str(c) for _, c in cs)
    s["col1"] = "".join(str(c + 1) for _, c in cs)
    s["col0_sp"] = " ".join(str(c) for _, c in cs)
    s["rowbits"] = "".join(str(r) for r, _ in cs)
    s["interleave0"] = "".join(f"{r}{c}" for r, c in cs)
    s["interleave1"] = "".join(f"{r}{c+1}" for r, c in cs)
    s["packbytes"] = bytes(r * 14 + c for r, c in cs).hex()
    s["decascii"] = ",".join(f"{r}{c}" for r, c in cs)
    return s

def board_chars(board, word):
    return word.upper()  # control: the letters themselves

def main():
    for bn, board in BOARDS.items():
        assert len(board) == 28, (bn, len(board))
        h = Harness(f"campaign_24_board_{bn}")
        # ---- Step 1: removed-material selector ----
        words = {"KING": "KING", "QUEEN": "QUEEN", "C": "C",
                 "KINGQUEENC": "KINGQUEENC", "QUEENKINGC": "QUEENKINGC"}
        for wn, w in words.items():
            cs = coords(board, w)
            if cs is None:
                print(f"[{bn}] {wn}: letters not all on board"); continue
            for sn, sv in serials(cs).items():
                h.try_pw(sv, f"rm:{wn}:{sn}", targets=["inner96"], kdfs=["m5", "s2"])
                h.try_pw(hashlib.sha256(sv.encode()).hexdigest(), f"rm:{wn}:{sn}:sha",
                         targets=["inner96"], kdfs=["m5", "s2"])
            h.try_pw(board_chars(board, w), f"rm:{wn}:ctrl", targets=["inner96"], kdfs=["m5", "s2"])
        # ---- Step 2: checkerboard numbering ----
        # rows = two straddling-checkerboard branches, columns = 14 positions.
        for row_assign in ((0, 1), (1, 0)):
            # each board char -> a digit stream: branch digit then position, per row
            digits_pos0 = []   # columns 0-based
            digits_pos1 = []
            for i, ch in enumerate(board):
                r, c = i // 14, i % 14
                branch = row_assign[r]
                digits_pos0.append(f"{branch}{c}")
                digits_pos1.append(f"{branch}{c+1}")
            for tag, seq in (("cb0", "".join(digits_pos0)), ("cb1", "".join(digits_pos1))):
                h.try_pw(seq, f"cb:{row_assign}:{tag}", targets=["inner96"], kdfs=["m5", "s2"])
                h.try_pw(hashlib.sha256(seq.encode()).hexdigest(), f"cb:{row_assign}:{tag}:sha",
                         targets=["inner96"], kdfs=["m5", "s2"])
                # packed nibbles where digits are 0-9
                if all(d.isdigit() for d in seq):
                    try:
                        s2 = seq if len(seq) % 2 == 0 else seq + "0"
                        pb = bytes(int(s2[k:k+2]) for k in range(0, len(s2), 2)).hex()
                        h.try_pw(pb, f"cb:{row_assign}:{tag}:nib", targets=["inner96"], kdfs=["m5", "s2"])
                    except Exception:
                        pass
        print(f"[{bn}] board = {board}")
        h.finish(f"campaign_24_board_{bn}")

if __name__ == "__main__":
    main()
