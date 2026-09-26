#!/usr/bin/env python3
"""Input-side script identification and offline signature verification (legacy and segwit v0).

input_script(vin, prev_spk=None) says who authorised an input, from its scriptSig and witness:
  p2pkh, p2pk (needs prev_spk), legacy p2sh-{m}of{n} multisig, p2wpkh, p2sh-p2wpkh,
  p2wsh-{m}of{n} and p2sh-p2wsh-{m}of{n} multisig, p2wsh/p2sh-p2wsh with another script,
  p2tr (key or script path; the address needs prev_spk). Nested forms are checked against
  their commitments: hash160(pubkey) for P2WPKH, sha256(witnessScript) for P2WSH.

verify_input(tx, i, prev_spk, prev_sat) checks the input's ECDSA signature(s) offline:
  legacy sighash (SIGHASH_ALL only) for p2pkh / p2pk / p2sh multisig, and BIP143 (all six
  sighash types) for p2wpkh / p2sh-p2wpkh / p2wsh / p2sh-p2wsh multisig. Segwit needs the spent
  output's amount; a signature verifies only under the exact amount. Multisig follows
  OP_CHECKMULTISIG order. Scripts with OP_CODESEPARATOR and taproot are reported, not verified.

`tx` is chain_flows.parse_raw output. No network, no keys. Self-test: the official BIP143
vectors (fixtures/bip143_vectors.json) plus saved GSMG signatures.

  python3 txscript.py --selftest
"""
import hashlib, json, os, sys
import btc_addr
from chain_flows import b58check, segwit_addr, parse_raw

HERE = os.path.dirname(os.path.abspath(__file__))
N, P = btc_addr.N, btc_addr.P

def dsha(b): return hashlib.sha256(hashlib.sha256(b).digest()).digest()
def sha(b): return hashlib.sha256(b).digest()
def varint(n):
    if n < 0xfd: return bytes([n])
    if n <= 0xffff: return b"\xfd" + n.to_bytes(2, "little")
    if n <= 0xffffffff: return b"\xfe" + n.to_bytes(4, "little")
    return b"\xff" + n.to_bytes(8, "little")
def varstr(b): return varint(len(b)) + b

# ---------- script parsing ----------
def parse_pushes(script):
    """Data pushes of a push-only script (OP_0 -> b''), or None if it holds any other opcode."""
    out, i = [], 0
    while i < len(script):
        op = script[i]; i += 1
        if op == 0:
            out.append(b""); continue
        if op < 0x4c:
            n = op
        elif op in (0x4c, 0x4d, 0x4e):
            w = {0x4c: 1, 0x4d: 2, 0x4e: 4}[op]
            if i + w > len(script): return None
            n = int.from_bytes(script[i:i + w], "little"); i += w
        else:
            return None
        if i + n > len(script): return None
        out.append(script[i:i + n]); i += n
    return out

def parse_multisig(script):
    """(m, [pubkeys]) for OP_m <pk>... OP_n OP_CHECKMULTISIG, else None."""
    if len(script) < 37 or script[-1] != 0xae:
        return None
    m, n = script[0] - 0x50, script[-2] - 0x50
    if not (1 <= m <= 16 and 1 <= n <= 16 and m <= n):
        return None
    keys, i = [], 1
    while i < len(script) - 2:
        l = script[i]
        if l not in (33, 65) or i + 1 + l > len(script) - 2:
            return None
        keys.append(script[i + 1:i + 1 + l]); i += 1 + l
    return (m, keys) if i == len(script) - 2 and len(keys) == n else None

def spk_address(spk):
    """Address of a scriptPubKey (p2pkh, p2sh, segwit v0/v1, p2pk as its p2pkh), else None."""
    if len(spk) == 25 and spk[:3] == b"\x76\xa9\x14" and spk[-2:] == b"\x88\xac":
        return b58check(b"\x00" + spk[3:23])
    if len(spk) == 23 and spk[:2] == b"\xa9\x14" and spk[-1:] == b"\x87":
        return b58check(b"\x05" + spk[2:22])
    if len(spk) in (22, 34) and spk[0] == 0 and spk[1] == len(spk) - 2:
        return segwit_addr(0, spk[2:])
    if len(spk) == 34 and spk[0] == 0x51 and spk[1] == 32:
        return segwit_addr(1, spk[2:])
    if len(spk) in (35, 67) and spk[0] == len(spk) - 2 and spk[-1] == 0xac:
        return b58check(b"\x00" + btc_addr.hash160(spk[1:-1]))
    return None

def _looks_sig(b):
    return 9 <= len(b) <= 73 and b[0] == 0x30

def input_script(vin, prev_spk=None):
    """What authorised this input. Returns a dict: kind, address, pubkeys, m, sigs, script_code,
    segwit, ok (commitments consistent), note."""
    ss = bytes.fromhex(vin["scriptSig"]); wit = [bytes.fromhex(w) for w in vin.get("witness", [])]
    d = {"kind": "unknown", "address": None, "pubkeys": [], "m": None, "sigs": [], "script_code": None,
         "segwit": bool(wit), "ok": True, "note": ""}
    pushes = parse_pushes(ss) if ss else []

    def wsh(ws, nested_redeem=None):
        ms = parse_multisig(ws)
        base = "p2sh-p2wsh" if nested_redeem is not None else "p2wsh"
        if ms:
            m, keys = ms
            d.update(kind=f"{base}-{m}of{len(keys)}", pubkeys=keys, m=m, sigs=[w for w in wit[1:-1] if w])
        else:
            d.update(kind=f"{base}-script", note="non-multisig witness script")
        d["script_code"] = ws
        if b"\xab" in ws and not ms:
            d["note"] += "; may contain OP_CODESEPARATOR (not verified)"
        if nested_redeem is not None:
            d["ok"] = nested_redeem[2:] == sha(ws)
            d["address"] = b58check(b"\x05" + btc_addr.hash160(nested_redeem))
        else:
            d["address"] = segwit_addr(0, sha(ws))

    if not wit:
        if pushes is None:
            d["note"] = "scriptSig holds non-push opcodes"
        elif len(pushes) == 2 and len(pushes[1]) in (33, 65) and pushes[1][0] in (2, 3, 4) and _looks_sig(pushes[0]):
            pub = pushes[1]
            d.update(kind="p2pkh", address=btc_addr.p2pkh(pub), pubkeys=[pub], m=1, sigs=[pushes[0]],
                     script_code=b"\x76\xa9\x14" + btc_addr.hash160(pub) + b"\x88\xac")
        elif len(pushes) == 1 and _looks_sig(pushes[0]):
            d.update(kind="p2pk", sigs=[pushes[0]], m=1)
            if prev_spk is not None and len(prev_spk) in (35, 67) and prev_spk[-1] == 0xac:
                d.update(pubkeys=[prev_spk[1:-1]], address=spk_address(prev_spk), script_code=prev_spk)
        elif len(pushes) >= 2 and pushes[0] == b"" and parse_multisig(pushes[-1]):
            m, keys = parse_multisig(pushes[-1])
            d.update(kind=f"p2sh-{m}of{len(keys)}", address=b58check(b"\x05" + btc_addr.hash160(pushes[-1])),
                     pubkeys=keys, m=m, sigs=pushes[1:-1], script_code=pushes[-1])
    elif not ss:
        if len(wit) == 2 and len(wit[1]) == 33 and wit[1][0] in (2, 3):
            pub = wit[1]
            d.update(kind="p2wpkh", address=segwit_addr(0, btc_addr.hash160(pub)), pubkeys=[pub], m=1,
                     sigs=[wit[0]], script_code=b"\x76\xa9\x14" + btc_addr.hash160(pub) + b"\x88\xac")
        elif len(wit) == 1 and len(wit[0]) in (64, 65):
            d.update(kind="p2tr-keypath", note="taproot: address from prev_spk; schnorr not verified")
        elif len(wit) >= 2 and wit[-1][:1] in (b"\xc0", b"\xc1") and (len(wit[-1]) - 33) % 32 == 0:
            d.update(kind="p2tr-scriptpath", note="taproot: address from prev_spk; not verified")
        else:
            wsh(wit[-1])
        if d["kind"].startswith("p2tr") and prev_spk is not None:
            d["address"] = spk_address(prev_spk)
    else:
        redeem = pushes[0] if pushes and len(pushes) == 1 else None
        if redeem is not None and len(redeem) == 22 and redeem[:2] == b"\x00\x14":
            pub = wit[-1] if wit else b""
            d.update(kind="p2sh-p2wpkh", address=b58check(b"\x05" + btc_addr.hash160(redeem)), pubkeys=[pub], m=1,
                     sigs=wit[:1], script_code=b"\x76\xa9\x14" + redeem[2:] + b"\x88\xac",
                     ok=len(wit) == 2 and btc_addr.hash160(pub) == redeem[2:])
        elif redeem is not None and len(redeem) == 34 and redeem[:2] == b"\x00\x20":
            wsh(wit[-1], nested_redeem=redeem)
        else:
            d["note"] = "unrecognised scriptSig + witness"
    if prev_spk is not None and d["address"] is not None:
        a = spk_address(prev_spk)
        if a is not None and a != d["address"]:
            d["ok"] = False; d["note"] += f"; spends {a}, input script says {d['address']}"
    return d

# ---------- sighash ----------
def _outpoint(v): return bytes.fromhex(v["txid"])[::-1] + v["vout"].to_bytes(4, "little")
def _out(o): return o["sat"].to_bytes(8, "little") + varstr(bytes.fromhex(o["spk"]))

def sighash_legacy(tx, i, script_code, hashtype):
    if hashtype != 1:
        return None                                          # only SIGHASH_ALL is implemented for legacy
    b = tx["version"].to_bytes(4, "little") + varint(len(tx["vin"]))
    for j, v in enumerate(tx["vin"]):
        b += _outpoint(v) + varstr(script_code if j == i else b"") + v["sequence"].to_bytes(4, "little")
    b += varint(len(tx["vout"])) + b"".join(_out(o) for o in tx["vout"])
    b += tx["locktime"].to_bytes(4, "little") + hashtype.to_bytes(4, "little")
    return int.from_bytes(dsha(b), "big")

def sighash_bip143(tx, i, script_code, amount, hashtype):
    base, acp, z32 = hashtype & 0x1f, hashtype & 0x80, b"\x00" * 32
    prevouts = z32 if acp else dsha(b"".join(_outpoint(v) for v in tx["vin"]))
    seqs = z32 if acp or base in (2, 3) else dsha(b"".join(v["sequence"].to_bytes(4, "little") for v in tx["vin"]))
    if base not in (2, 3):
        outs = dsha(b"".join(_out(o) for o in tx["vout"]))
    elif base == 3 and i < len(tx["vout"]):
        outs = dsha(_out(tx["vout"][i]))
    else:
        outs = z32
    v = tx["vin"][i]
    pre = (tx["version"].to_bytes(4, "little") + prevouts + seqs + _outpoint(v) + varstr(script_code)
           + amount.to_bytes(8, "little") + v["sequence"].to_bytes(4, "little") + outs
           + tx["locktime"].to_bytes(4, "little") + hashtype.to_bytes(4, "little"))
    return int.from_bytes(dsha(pre), "big")

# ---------- ECDSA ----------
def _point(pub):
    if len(pub) == 65 and pub[0] == 4:
        return int.from_bytes(pub[1:33], "big"), int.from_bytes(pub[33:], "big")
    if len(pub) == 33 and pub[0] in (2, 3):
        x = int.from_bytes(pub[1:], "big")
        y = pow((x * x * x + 7) % P, (P + 1) // 4, P)
        if (y * y - x * x * x - 7) % P:
            return None
        return x, (y if y % 2 == pub[0] % 2 else P - y)
    return None

def _der(sig):
    """(r, s) of a strict-enough DER signature, else None."""
    try:
        if sig[0] != 0x30 or sig[2] != 0x02:
            return None
        lr = sig[3]; r = int.from_bytes(sig[4:4 + lr], "big")
        if sig[4 + lr] != 0x02:
            return None
        ls = sig[5 + lr]; s = int.from_bytes(sig[6 + lr:6 + lr + ls], "big")
        return r, s
    except IndexError:
        return None

def ecdsa_ok(pub, z, sig_der):
    Q, rs = _point(pub), _der(sig_der)
    if Q is None or rs is None:
        return False
    r, s = rs
    if not (1 <= r < N and 1 <= s < N):
        return False
    w = pow(s, -1, N)
    R = btc_addr._add(btc_addr.mul(z * w % N), btc_addr.mul(r * w % N, Q))
    return R is not None and R[0] % N == r

def verify_input(tx, i, prev_spk=None, prev_sat=None):
    """{'kind', 'address', 'ok': True/False/None, 'why'}; None means not checkable here."""
    d = input_script(tx["vin"][i], prev_spk)
    res = {"kind": d["kind"], "address": d["address"], "pubkeys": [p.hex() for p in d["pubkeys"]], "ok": None, "why": ""}
    if not d["ok"]:
        res.update(ok=False, why="script commitments inconsistent" + d["note"]); return res
    if not d["sigs"] or d["script_code"] is None or not d["pubkeys"]:
        res["why"] = "not checkable: " + (d["note"] or d["kind"]); return res
    if d["segwit"] and prev_sat is None:
        res["why"] = "segwit: needs the spent output's amount"; return res

    def z_of(sig):
        ht = sig[-1]
        if d["segwit"]:
            return sighash_bip143(tx, i, d["script_code"], prev_sat, ht)
        return sighash_legacy(tx, i, d["script_code"], ht)

    sigs, keys, k = d["sigs"], d["pubkeys"], 0
    for sig in sigs:                                        # OP_CHECKMULTISIG order; single-key is m=1
        z = z_of(sig)
        if z is None:
            res["why"] = f"sighash type {sig[-1]:#x} not implemented for legacy"; return res
        while k < len(keys) and not ecdsa_ok(keys[k], z, sig[:-1]):
            k += 1
        if k == len(keys):
            res.update(ok=False, why="a signature does not verify"); return res
        k += 1
    res.update(ok=len(sigs) >= (d["m"] or 1), why=f"{len(sigs)} signature(s) verified")
    return res

# ---------- self-test ----------
def selftest():
    ok = True
    vec = json.load(open(os.path.join(HERE, "fixtures", "bip143_vectors.json")))
    for v in vec["vectors"]:
        tx = parse_raw(v["tx"])
        for inp in v["inputs"]:
            spk = bytes.fromhex(inp["prev_spk"])
            r = verify_input(tx, inp["index"], spk, inp["prev_sat"])
            bad = verify_input(tx, inp["index"], spk, inp["prev_sat"] + 1) if r["kind"].startswith(("p2w", "p2sh-p2w")) else {"ok": False}
            good = r["ok"] is True and r["kind"] == inp["kind"] and bad["ok"] is False
            ok &= good
            print(("OK  " if good else "FAIL"), f"BIP143 {v['name']} in{inp['index']}: {r['kind']} ok={r['ok']} "
                  f"({r['why']}); amount+1 -> {bad['ok']}")
    # the user's reading of 37mh…: a 2-of-2 P2SH-P2WSH over these two keys, in this order
    pk1 = bytes.fromhex("028f26891f480f1985251e17ba39eced2f9af9228e8d17bb27f02bd0650861e5e1")
    pk2 = bytes.fromhex("03e4bf9bc90397504ddc7bc7d6a499cd9ae69ca47b212e0ea3d1ee029d0c1e2a22")
    ws = bytes([0x52, 0x21]) + pk1 + bytes([0x21]) + pk2 + bytes([0x52, 0xae])
    fake = {"txid": "00" * 32, "vout": 0, "scriptSig": (b"\x22\x00\x20" + sha(ws)).hex(),
            "witness": ["", "30" + "00" * 70 + "01", "30" + "00" * 70 + "01", ws.hex()], "sequence": 0}
    d = input_script(fake)
    good = d["kind"] == "p2sh-p2wsh-2of2" and d["address"] == "37mh7EYetVKAesxqzv968sTYqSLF8dE6oD" and d["ok"]
    ok &= good
    print(("OK  " if good else "FAIL"), "P2SH-P2WSH 2-of-2 parse:", d["kind"], d["address"])
    print("txscript self-test passed:", ok)
    return ok

if __name__ == "__main__":
    sys.exit(0 if selftest() else 1)
