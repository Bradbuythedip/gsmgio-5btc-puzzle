#!/usr/bin/env python3
"""Campaign 28: the Base58 frame (user-supplied, 2026-09-26).

Thesis under test: slot A is the COLOUR INTEGER (f73d92) rather than a spelling of
"yellowblueprimes", and the puzzle's numbers should be written in Bitcoin Base58.
Also tests "zeroed out" = delete the Base58-illegal set {0,O,I,l} from a named string.

Pre-registered, bounded. Every candidate raw + sha256hex, EVP-MD5 + EVP-SHA256, against
all three outstanding locks; plus the offline address oracle (prize / second / 1NULY7).
Nothing here invents a new operand: A/B/C come from the frozen sheet + the colour frame.
"""
import os, sys, hashlib, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from aes_try import Harness
from addr_check import check

B58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58_int(n):
    if n == 0: return B58[0]
    s = ''
    while n > 0:
        n, r = divmod(n, 58); s = B58[r] + s
    return s
ILLEGAL = set('0OIl')
def zero_out(s):
    return ''.join(c for c in s if c not in ILLEGAL)

# --- frozen slot sets (sheet + colour frame) ---
F = 0xf73d92; COMP = 0x08c26d
A = {
    'f73d92': 'f73d92', 'F73D92': 'F73D92', 'dec16203154': '16203154',
    'b58-2S3dj': b58_int(F), '0xf73d92': '0xf73d92',
    'comp08c26d': '08c26d', 'compdec574061': '574061', 'comp-b58': b58_int(COMP),
    'prime445': '445', 'prime-b58': b58_int(445), 'primebits': '110111101',
    'zlabel-yeowbueprimes': 'yeowbueprimes', 'zlabel-dec': '82101348098033013316316',
}
B = {
    'B0': 'matrixsumlist', 'B1': '610876654997879', 'B2': '8108108736759668',
    'B3': '6108766549978798108108736759668',
    'B1-b58': b58_int(610876654997879), 'B2-b58': b58_int(8108108736759668),
    'B3-b58': b58_int(6108766549978798108108736759668),
}
C = {
    'C0': 'lastwordsbeforearchichoice', 'C1': 'ireallyhopeyouretheone',
    'C3': 'ciaobellao',
    'C2': 'hopeitisthequintessentialhumandelusionsimultaneouslythesourceofyourgreateststrengthandyourgreatestweakness',
}
# add "zeroed out" variants of each slot value (delete {0,O,I,l})
for d in (A, B, C):
    for k in list(d):
        z = zero_out(d[k])
        if z != d[k] and z:
            d[k + '|zero'] = z

TARGETS = ['cosmic', 'inner96', 'miniAB']
KDFS = ['m5', 's2']

def main():
    h = Harness('campaign_28_base58')
    addr_cands = []
    # A alone
    for ak, av in A.items():
        h.try_pw(av, f'A:{ak}', targets=TARGETS, kdfs=KDFS)
        h.try_pw(hashlib.sha256(av.encode()).hexdigest(), f'A:{ak}:sha', targets=TARGETS, kdfs=KDFS)
        addr_cands.append((f'A:{ak}', av.encode()))
    # three-slot combine A||B||C (the sheet's §6 join: no separator)
    n = 0
    for (ak, av), (bk, bv), (ck, cv) in itertools.product(A.items(), B.items(), C.items()):
        s = av + bv + cv
        h.try_pw(s, f'ABC:{ak}:{bk}:{ck}', targets=TARGETS, kdfs=KDFS)
        h.try_pw(hashlib.sha256(s.encode()).hexdigest(), f'ABC:{ak}:{bk}:{ck}:sha', targets=TARGETS, kdfs=KDFS)
        n += 1
    print('combine candidates:', n, ' A-alone:', len(A))
    h.finish('campaign_28_base58')
    # address oracle: A alone + A||B0||C0 for each A (bounded)
    for ak, av in A.items():
        s = av + 'matrixsumlist' + 'lastwordsbeforearchichoice'
        addr_cands.append((f'ABC0:{ak}', s.encode()))
    print('address candidates:', len(addr_cands))
    print('address matches:', check(addr_cands))

if __name__ == '__main__':
    main()
