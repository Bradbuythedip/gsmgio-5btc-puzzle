import hashlib
from coincurve import PrivateKey
B58='123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
def b58encode(b):
    n=int.from_bytes(b,'big'); s=''
    while n>0: n,r=divmod(n,58); s=B58[r]+s
    pad=len(b)-len(b.lstrip(b'\0'))
    return '1'*pad+s
def hash160(b): return hashlib.new('ripemd160', hashlib.sha256(b).digest()).digest()
def p2pkh(pub): 
    h=b'\x00'+hash160(pub); return b58encode(h+hashlib.sha256(hashlib.sha256(h).digest()).digest()[:4])
N=0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
def addrs_from_key(k32):
    k=int.from_bytes(k32,'big')
    if k==0 or k>=N: return None,None
    pk=PrivateKey(k32)
    return p2pkh(pk.public_key.format(compressed=True)), p2pkh(pk.public_key.format(compressed=False))
def sha_key(s): return hashlib.sha256(s.encode() if isinstance(s,str) else s).digest()
if __name__=='__main__':
    tests=[('causality','1Jqq37KkZEt4F3Dt6qXdtyiMEFBBdawbkJ'),
           ('theflowerblossomsthroughwhatseemstobeaconcretesurface','1AD2wfwXukZ1kUAy848hTQQ72aSBZPB75r'),
           ('jacquefrescogiveitjustonesecondheisenbergsuncertaintyprinciple','1K23RS1y2fnuZRkhw5nUpFr5Jk5WN11Zeq'),
           ('15165943121972409169171213758951813141543131412428154191312181219433121171617137149110916631213131281491109166131412199114371612126021664313711154112','18CchrjA3Uzfrzy4DFqao9ric6YfK4hjdc'),
           ('1GSMG1JC9wtdSwfwApgj2xcmJPAwx7prBe','1GyT5WrLYpwFkuiVoPDJZa1Q6jtjbjuBff')]
    for s,exp in tests:
        c,u=addrs_from_key(sha_key(s)); print(s[:40], c, u, "OK" if c==exp else "MISMATCH")
    raw=b'gsmg.io/theseedisplanted'
    k=raw.rjust(32,b'\0'); c,u=addrs_from_key(k); print("raw padded:", c, u, c=='148XH2YBmLr4oAJXQcG84FpNYoBmqnVPHQ')
    bits=''.join(format(b,'08b') for b in raw)[::-1]
    k=int(bits,2).to_bytes(32,'big'); c,u=addrs_from_key(k); print("bits reversed:", c, u, c=='13HGhjkmKUkP8sk9k63BLmhkxRjy7uK4Rp')
