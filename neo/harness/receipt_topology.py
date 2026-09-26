#!/usr/bin/env python3
"""Receipt-topology audit of the creator's on-chain record (tick 88). No AES, no key search.

User-relayed triple-entry reading (Grigg 2005, "the receipt is the transaction") of "THE PRIVATE
KEYS BELONG TO HALF AND BETTER HALF AND THEY ALSO NEED FUNDS TO LIVE": the two halves do not
combine algebraically, they transact, and the chain is their shared signed receipt. This reads
only the raw transactions saved in the repo. For each one it records who authorised it (input
signers), who the counterparty is (outputs), what memo it carries (OP_RETURN), and which saved
transactions are hash-linked: a spend signs its outpoints, so its signature commits to the
earlier transaction and to that transaction's memo. Legacy P2PKH signatures are re-verified.
Creator transactions recorded in the ledger without raw hex are listed separately with their tick.

Pre-stated questions, answered mechanically at the end:
  Q1 co-signature  does any saved tx have BOTH halves as inputs (both authorise)?
  Q2 same-tx memo  does any saved tx carry both halves AND an OP_RETURN?
  Q3 linked memo   does a half -> better-half tx spend an output of a memo-carrying tx?
  Q4 better half   has 17ucy1 signed anything in the saved record?

  python3 receipt_topology.py
"""
import ast, hashlib, os, sys
import btc_addr
import verify_halving_sigs as V
from chain_flows import parse_raw, script_info, b58check, segwit_addr
from campaign_01 import PHASE22

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
SAVED = ["materials/chain/tx_halving_optreturn.hex", "materials/chain/tx_halving_spend.hex",
         "materials/chain/tx_halving2024_spend.hex", "../unverified/tx_good_job_neo_2020.hex",
         "../unverified/tx_8aaa96d3_neo_wallet.hex"]
HALF = "1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe"
BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
CREATOR = "3GSMG24TujqfMJG1kQoBX18DzJHQLeJYMK"
SEED = b"gsmg.io/theseedisplanted"

def _literal(module, name):
    """Read a list literal from a campaign's source without importing it (importing runs it)."""
    tree = ast.parse(open(os.path.join(HERE, module)).read())
    return next(ast.literal_eval(n.value) for n in tree.body
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == name for t in n.targets))
CHECKPOINT_ANSWERS = _literal("campaign_42_checkpoints.py", "CANDIDATES")

# ledger-recorded values this audit re-derives offline
TICK59_PREFIXES = ["1Jqq37", "1GyT5W", "18Cchr", "1K23RS", "1AD2wf", "1M5ypv"]   # CHECKPOINT_ANSWERS + PHASE22
TICK52_POINTS = {"Q-G": "1G1kRAFR68y6CUq1SAJMzHmjd6sEEgtVUT", "Q/2": "16eEXbSuKN8tvcos1iKjdju6dAaWWRBMEs",
                 "2Q": "1KHMK2C8uBptRz67FbrXy43yHzhZG16Hbm", "Q+G": "1PhXF3xVQ8Sg9FomBcmRwRbvvGfm3Y2os1"}

# creator transactions recorded in the ledger whose raw hex is not in the repo
RECORDED_ONLY = [
    ("2018-01-11", "1EtbTv…", "-", "1GSMG1CLx… 1,337,000 sat", "38"),
    ("2019-04-13", "1EtbTv…", "-", "prize 1GSMG1… 5.0 BTC (block 571497)", "38"),
    ("2020-03-24", "3GSMG24T…", "six checkpoint memos", "compressed P2PKH(sha256(answer)), 1000 sat each", "38, 59"),
    ("2020-04-07", "3GSMG24T…", "none (bare)", "1NULY7… 1050 sat (answer not identified)", "38"),
    ("2021-07-18", "3GSMG24T…", "GSMG.io neighbors, half and double", "Q-G, Q/2, 2Q, Q+G, 5000 sat each", "38, 52, 53"),
    ("pre-2024", "?", "?", "81d35929…:0 and f28b0b68…:0, consumed by the 2024 split; parents not saved", "72"),
]

def h160(b): return btc_addr.hash160(b)

def point_addrs(P):
    x, y = P
    unc = b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")
    comp = bytes([2 + (y & 1)]) + x.to_bytes(32, "big")
    return btc_addr.p2pkh(comp), btc_addr.p2pkh(unc)

def short(s, n=28): return s if len(s) <= n else s[:n] + "…"

def load_saved():
    txs = []
    for rel in SAVED:
        for line in open(os.path.join(NEO, rel)):
            line = line.strip()
            if line and not line.startswith("#"):
                tx = parse_raw(line); tx["file"] = rel; txs.append(tx)
    return txs

def signer(vin):
    """(kind, address, pubkey) of whoever authorised this input; pubkey is None for multisig and
    unknown types. Full detail (all pubkeys, m-of-n, commitments) is txscript.input_script(vin)."""
    import txscript
    d = txscript.input_script(vin)
    return d["kind"], d["address"], (d["pubkeys"][0] if len(d["pubkeys"]) == 1 else None)

def uncompressed(pub):
    if len(pub) == 65:
        return pub
    x = int.from_bytes(pub[1:], "big"); P = btc_addr.P
    y = pow((x * x * x + 7) % P, (P + 1) // 4, P)
    if y % 2 != pub[0] % 2:
        y = P - y
    return b"\x04" + x.to_bytes(32, "big") + y.to_bytes(32, "big")

def verify_legacy(raw_hex):
    """Per-input SIGHASH_ALL verification for legacy P2PKH txs; None for segwit (BIP143 needs amounts)."""
    raw = bytes.fromhex(raw_hex)
    if raw[4] == 0 and raw[5] == 1:
        return None
    ver, ins, outs, lt = V.parse(raw)
    res = []
    for k, (prev, ss, seq) in enumerate(ins):
        sig, pub = V.pushes(ss)
        der, ht = sig[:-1], sig[-1]
        spk = b"\x76\xa9\x14" + h160(pub) + b"\x88\xac"
        r, s = V.der_rs(der)
        z = V.sighash_all(ver, ins, outs, lt, k, spk, ht)
        res.append(ht == 1 and V.verify_own(uncompressed(pub), z, r, s))
    return res

def build_labels(Q):
    lab = {HALF: "HALF (prize)", BETTER: "BETTER HALF", CREATOR: "creator vanity 3GSMG24T",
           "1EtbTvVB8QTGN4mduSdy7n4cZQm4iYTpQ1": "2019 funder", "1NULY7DhzuNvSDtPkFzNo6oRTZQWBqXNE9": "open checkpoint"}
    derived = {}
    for a in CHECKPOINT_ANSWERS + [PHASE22]:
        c, u = btc_addr.addrs(int(hashlib.sha256(a.encode()).hexdigest(), 16))
        lab.setdefault(c, f"answer-key sha256({short(a, 20)})"); derived[a] = c
        lab.setdefault(u, f"answer-key sha256({short(a, 20)}), uncompressed")
    n = int.from_bytes(SEED, "big")
    for tag, k in (("seed raw key", n), ("seed raw key, bits reversed", int(format(n, "0192b")[::-1], 2))):
        for a in btc_addr.addrs(k):
            lab.setdefault(a, tag)
    G = (btc_addr.GX, btc_addr.GY); negG = (btc_addr.GX, btc_addr.P - btc_addr.GY)
    pts = {"Q-G": btc_addr._add(Q, negG), "Q/2": btc_addr.mul(pow(2, -1, btc_addr.N), Q),
           "2Q": btc_addr._add(Q, Q), "Q+G": btc_addr._add(Q, G)}
    qaddr = {}
    for tag, P in pts.items():
        c, u = point_addrs(P); qaddr[tag] = u
        lab.setdefault(u, f"prize point {tag}"); lab.setdefault(c, f"prize point {tag} (compressed)")
    return lab, derived, qaddr

def main():
    txs = load_saved()
    by_id = {t["txid"]: t for t in txs}
    for t in txs:
        t["signers"] = [signer(v) for v in t["vin"]]
        t["outs"] = [(o["n"], o["sat"]) + script_info(bytes.fromhex(o["spk"])) for o in t["vout"]]
        t["memos"] = [d.decode("latin1") for _, _, kind, _, d in t["outs"] if kind == "op_return"]
        t["sigs"] = verify_legacy(t["raw"])
    split = next(t for t in txs if t["txid"].startswith("2aa9a4a9"))
    Q = next((int.from_bytes(p[1:33], "big"), int.from_bytes(p[33:65], "big"))
             for k, a, p in split["signers"] if a == HALF and len(p) == 65)
    lab, derived, qaddr = build_labels(Q)
    L = lambda a: f"{a} [{lab[a]}]" if a in lab else str(a)

    print("== offline re-derivations of ledger-recorded addresses ==")
    for a, pre in zip(CHECKPOINT_ANSWERS + [PHASE22], TICK59_PREFIXES):
        print(f"  tick 59  sha256({short(a, 24)!r:30s}) -> {derived[a]}  matches {pre}…: {derived[a].startswith(pre)}")
    for tag, want in TICK52_POINTS.items():
        print(f"  tick 52  {tag:4s} -> {qaddr[tag]}  matches: {qaddr[tag] == want}")

    print(f"\n== {len(txs)} saved raw transactions, decoded ==")
    for t in txs:
        auth = {a for _, a, _ in t["signers"]}
        tier = "creator-signed" if auth & {HALF, CREATOR} else "not creator-signed"
        print(f"\n[{t['txid'][:16]}…] v{t['version']} {'segwit' if t['segwit'] else 'legacy'} "
              f"locktime {t['locktime']}  ({t['file']})  -> {tier}")
        for i, (v, (kind, a, pub)) in enumerate(zip(t["vin"], t["signers"])):
            sig = ("not verifiable offline (BIP143 needs input amounts)" if t["sigs"] is None
                   else f"signature verified: {t['sigs'][i]}")
            link = " <- SAVED PARENT" if v["txid"] in by_id else ""
            print(f"   in  {v['txid'][:16]}…:{v['vout']} seq {v['sequence']:08x}  signer {L(a)} ({kind}); {sig}{link}")
        for n, sat, kind, a, d in t["outs"]:
            print(f"   out #{n} " + (f'OP_RETURN "{d.decode("latin1")}"' if kind == "op_return" else f"{sat} sat -> {L(a)}"))

    print("\n== hash links between saved transactions (the child's signature commits to the parent) ==")
    links = []
    for t in txs:
        for i, v in enumerate(t["vin"]):
            if v["txid"] in by_id:
                p = by_id[v["txid"]]; _, sat, kind, a, _ = p["outs"][v["vout"]]
                signed = t["sigs"][i] if t["sigs"] is not None else None
                links.append((p, t, v["vout"], signed))
                print(f"  {p['txid'][:12]}… memo {p['memos'] or '-'} out #{v['vout']} ({sat} sat -> {L(a)})\n"
                      f"     spent by {t['txid'][:12]}… signer {L(t['signers'][i][1])}, signature over this outpoint verified: {signed}")

    print("\n== creator transactions recorded in the ledger, raw hex not in the repo ==")
    for row in RECORDED_ONLY:
        print("  {:10s}  {:10s} memo: {:36s} -> {}  (tick {})".format(*row))

    def signs(t, a): return any(x == a for _, x, _ in t["signers"])
    def pays(t, a): return any(x == a for _, _, _, x, _ in t["outs"])
    q1 = [t["txid"][:12] for t in txs if signs(t, HALF) and signs(t, BETTER)]
    q2 = [t["txid"][:12] for t in txs if (signs(t, HALF) or pays(t, HALF)) and (signs(t, BETTER) or pays(t, BETTER)) and t["memos"]]
    hb = [t for t in txs if signs(t, HALF) and pays(t, BETTER)]
    q3 = [(p["txid"][:12], p["memos"], c["txid"][:12], ok) for p, c, _, ok in links if c in hb and p["memos"]]
    q4 = [t["txid"][:12] for t in txs if signs(t, BETTER)]
    print("\n== pre-stated questions ==")
    print(f"  half -> better-half payments in the saved record: {[t['txid'][:12] + '… lt ' + str(t['locktime']) for t in hb]}")
    print(f"  Q1 both halves co-sign one tx:            {q1 or 'NO'}")
    print(f"  Q2 both halves + OP_RETURN in one tx:     {q2 or 'NO'}")
    print(f"  Q3 half->better-half spends a memo'd tx:  {q3 or 'NO'}")
    print(f"  Q4 17ucy1 has signed anything:            {q4 or 'NO (receive-only; no pubkey, no signature)'}")
    ok = all(derived[a].startswith(p) for a, p in zip(CHECKPOINT_ANSWERS + [PHASE22], TICK59_PREFIXES)) \
        and all(qaddr[k] == v for k, v in TICK52_POINTS.items()) \
        and all(all(t["sigs"]) for t in hb)
    print("\nre-derivations and half->better-half signatures all check:", ok)
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
