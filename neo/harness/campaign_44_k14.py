#!/usr/bin/env python3
"""Campaign 44: the K14 edge-space (multiplicity) reading, pre-registered in
intake/2026-09-26-k14/PREREG.md. User-directed; does not reopen the parked corpus.

The hypothesis: the 91-symbol streams are edge labels on K14 (C(14,2) = 91), the VIC
one-digit/two-digit split is a 33-edge mask, the 24 coloured cells are edges, and some graph
invariant of that state "reduces to" a known macro label or opens a lock.

Three frozen checks, nothing else:
  A. structure  - is any observed graph atypical against its null (uniform 33-edge subsets
                  for the mask, composition-preserving shuffles for weighted streams)?
                  Bonferroni per family at alpha = 0.01.
  B. text       - do the fixed mod-26 renderings of the fixed integer sequences contain
                  YOUWON / HALF / YINYANG, and at what null rate?
  C. crypto     - the fixed serializations through gate.py's frozen decrypt path, the P32T
                  freeze oracle, and prize / better-half address checks.

Needs numpy and networkx in addition to pycryptodome.

  python3 campaign_44_k14.py --selftest   known-answer tests for every invariant
  python3 campaign_44_k14.py --describe   the objects only (no invariants)
  python3 campaign_44_k14.py              the full pre-registered run
"""
import hashlib, itertools, json, math, os, re, sys, time
from fractions import Fraction
import numpy as np
import networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
NEO = os.path.join(HERE, "..")
REPO = os.path.join(NEO, "..")
OUT = os.path.join(NEO, "attempts", "campaign_44_k14.jsonl")
SUMMARY = os.path.join(NEO, "attempts", "campaign_44_k14_summary.json")

SEED = 20260926
N_NULL_U = 20000        # uniform 33-edge subsets (unweighted family)
N_NULL_W = 50000        # composition-preserving shuffles per weighted stream
ALPHA = 0.01
TARGET_WORDS = ("YOUWON", "HALF", "YINYANG")
BETTER = "17ucy1K9ZUAaoY6JVtM932W9jUp5LXfyHa"
SECP_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

V = 14
FULL = (1 << V) - 1

# ---------------------------------------------------------------- objects

def load_objects():
    grid = json.load(open(os.path.join(NEO, "materials/primary/matrix_grid_spiral_colors.json")))
    spiral = [tuple(x) for x in grid["spiral"]]              # (row, col), ccw from (0,0)
    placements = {
        "RM":  [(i, j) for i in range(V) for j in range(i + 1, V)],
        "CM":  [(i, j) for j in range(V) for i in range(j)],
        "SPU": [(r, c) for r, c in spiral if c > r],
        "SPL": [(c, r) for r, c in spiral if c < r],
    }
    for p, e in placements.items():
        assert len(e) == 91 and len(set(e)) == 91, p

    soup = open(os.path.join(NEO, "materials/primary/salphaseion_soup_space_separated.txt")).read().split()
    dbbi, faed = soup[:91], soup[195:765]
    tape = dbbi + faed
    layers = [tape[91 * k: 91 * (k + 1)] for k in range(7)]

    vic_line = [l.strip() for l in open(os.path.join(REPO, "phase3-assets/phase3.2.txt"), encoding="latin-1")
                if re.fullmatch(r"\d{100,}", l.strip())][0]
    board = dict(zip("02356789", "FUBCDORA"))
    board.update({f"1{i}": ch for i, ch in enumerate(".LETHINGKY")})
    board.update({f"4{i}": ch for i, ch in enumerate("MVPS.JQZXW")})
    toks, i = [], 0
    while i < len(vic_line):
        t = vic_line[i:i + 2] if vic_line[i] in "14" else vic_line[i]
        toks.append(t); i += len(t)
    sent = "".join(board[t] for t in toks)
    assert sent == ("INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALF"
                    "ANDTHEYALSONEEDFUNDSTOLIVE"), sent
    mask = [1 if len(t) == 1 else 0 for t in toks]
    assert len(mask) == 91 and sum(mask) == 33

    d1 = [ord(c) - 96 for c in dbbi]                         # a=1 .. i=9
    v1 = [ord(c) - 64 for c in sent]                         # A=1 .. Z=26
    res = [(d - v) % 26 for d, v in zip(d1, v1)]             # rendered A=0
    res_txt = "".join(chr(65 + r) for r in res)
    assert res_txt[21:27] == "YOUWON", res_txt

    col = {tuple(c) for c in grid["yellow"]} | {tuple(c) for c in grid["blue"]}
    assert len(col) == 24
    colU = [(r, c) for r, c in col if c > r]
    colL = [(r, c) for r, c in col if c < r]

    streams = {f"L{k + 1}": [ord(c) - 97 for c in layers[k]] for k in range(7)}   # a=0 .. i=8
    streams["VIC"] = v1                                                            # A=1 .. Z=26
    streams["RES"] = res                                                           # A=0 .. Z=25
    alph = {**{f"L{k + 1}": "abcdefghi" for k in range(7)},
            "VIC": "@ABCDEFGHIJKLMNOPQRSTUVWXYZ", "RES": "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
    return dict(placements=placements, mask=mask, sent=sent, res_txt=res_txt, streams=streams,
                alph=alph, colU=colU, colL=colL, spiral=spiral)

def english_windows(maxn=200):
    """Letters of the verbatim creator-message column, non-overlapping 91-letter windows."""
    txt = []
    for line in open(os.path.join(NEO, "materials/primary/CREATOR-LOG_transcript_445_messages.md"), encoding="utf-8"):
        cells = line.split("|")
        if len(cells) > 5 and re.fullmatch(r"\s*\d+\s*", cells[1]) and "[no text]" not in cells[4]:
            txt.append(cells[4])
    L = re.sub(r"[^A-Z]", "", " ".join(txt).upper())
    return [L[91 * k: 91 * (k + 1)] for k in range(min(maxn, len(L) // 91))]

# ---------------------------------------------------------------- exact invariants

def adj_from_edges(edges):
    A = [[0] * V for _ in range(V)]
    for i, j in edges:
        A[i][j] = A[j][i] = 1
    return A

def degrees(A):
    return [sum(r) for r in A]

def components(A):
    seen, comps = set(), 0
    for s in range(len(A)):
        if s in seen: continue
        comps += 1; stack = [s]; seen.add(s)
        while stack:
            u = stack.pop()
            for w in range(len(A)):
                if A[u][w] and w not in seen:
                    seen.add(w); stack.append(w)
    return comps

def bareiss_det(M):
    """Exact integer determinant."""
    M = [row[:] for row in M]; n = len(M)
    if n == 0: return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            sw = next((r for r in range(k + 1, n) if M[r][k] != 0), None)
            if sw is None: return 0
            M[k], M[sw] = M[sw], M[k]; sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]

def laplacian(W):
    n = len(W)
    return [[(sum(W[i]) - W[i][i]) if i == j else -W[i][j] for j in range(n)] for i in range(n)]

def spanning_trees(W):
    """Matrix-tree theorem; weighted if W has integer weights (sum over trees of weight products)."""
    L = laplacian(W)
    return bareiss_det([row[1:] for row in L[1:]])

def ham_paths_and_cycles(A):
    n = len(A); full = (1 << n) - 1
    nb = [sum(1 << w for w in range(n) if A[v][w]) for v in range(n)]
    # all starts: undirected Hamiltonian paths
    dp = [[0] * n for _ in range(1 << n)]
    for v in range(n): dp[1 << v][v] = 1
    for m in range(1, 1 << n):
        row = dp[m]
        for v in range(n):
            c = row[v]
            if not c: continue
            ext = nb[v] & ~m
            while ext:
                b = ext & -ext; w = b.bit_length() - 1
                dp[m | b][w] += c; ext ^= b
    paths = sum(dp[full]) // 2 if n > 1 else 1
    # start fixed at 0: Hamiltonian cycles
    dp0 = {1: [1] + [0] * (n - 1)}
    for m in range(1, 1 << n):
        if not (m & 1) or m not in dp0: continue
        row = dp0[m]
        for v in range(n):
            c = row[v]
            if not c: continue
            ext = nb[v] & ~m
            while ext:
                b = ext & -ext; w = b.bit_length() - 1
                dp0.setdefault(m | b, [0] * n)[w] += c; ext ^= b
    last = dp0.get(full, [0] * n)
    cycles = sum(last[v] for v in range(1, n) if A[0][v]) // 2 if n >= 3 else 0
    return paths, cycles

def graph_invariants(edges):
    A = adj_from_edges(edges)
    G = nx.Graph(); G.add_nodes_from(range(V)); G.add_edges_from(edges)
    deg = degrees(A)
    c = components(A)
    An = np.array(A, dtype=float)
    Ln = np.diag(An.sum(1)) - An
    spec = np.linalg.eigvalsh(Ln)
    tau = spanning_trees(A)
    hp, hc = ham_paths_and_cycles(A)
    m = len(edges)
    return {
        "edges": m, "deg": deg, "deg_sorted": sorted(deg, reverse=True),
        "deg_var": float(np.var(deg)), "components": c, "connected": c == 1,
        "edge_conn": nx.edge_connectivity(G) if c == 1 else 0,
        "vertex_conn": nx.node_connectivity(G) if c == 1 else 0,
        "triangles": int(round(np.trace(An @ An @ An) / 6)),
        "cycle_rank": m - V + c, "tau": tau, "log_tau": math.log(tau) if tau > 0 else float("-inf"),
        "ham_paths": hp, "ham_cycles": hc,
        "diameter": nx.diameter(G) if c == 1 else None, "bipartite": nx.is_bipartite(G),
        "lap_spectrum": [round(float(x), 6) for x in spec], "lambda2": float(spec[1]),
    }

def weighted_invariants(stream, placement):
    W = [[0] * V for _ in range(V)]
    for (i, j), w in zip(placement, stream):
        W[i][j] = W[j][i] = w
    s = [sum(r) for r in W]
    Wn = np.array(W, dtype=float)
    spec = np.linalg.eigvalsh(np.diag(Wn.sum(1)) - Wn)
    tw = spanning_trees(W)
    return {"strength": s, "strength_var": float(np.var(s)), "total": sum(stream),
            "lambda2": float(spec[1]), "lambda_max": float(spec[-1]),
            "tau_w": tw, "log_tau_w": math.log(tw) if tw > 0 else float("-inf")}

# ---------------------------------------------------------------- batched null (numpy)

IU = np.array([(i, j) for i in range(V) for j in range(i + 1, V)])

def batch_adj(vals):
    """vals (B, 91) in RM edge order -> symmetric (B, 14, 14)."""
    B = vals.shape[0]
    W = np.zeros((B, V, V), dtype=np.float64)
    W[:, IU[:, 0], IU[:, 1]] = vals
    W[:, IU[:, 1], IU[:, 0]] = vals
    return W

def batch_spectral(W):
    L = np.diag(np.ones(V))[None] * W.sum(2)[:, :, None] - W
    spec = np.linalg.eigvalsh(L)
    sign, logdet = np.linalg.slogdet(L[:, 1:, 1:])
    logtau = np.where(sign > 0, logdet, -np.inf)
    # a tree count is an integer >= 1 when positive; tiny float noise near 0 means disconnected
    logtau = np.where(logtau < -1e-6, -np.inf, logtau)
    return spec, logtau

def batch_ham_paths(Abool):
    """Exact undirected Hamiltonian-path counts for a batch of 14-vertex graphs."""
    B = Abool.shape[0]
    A = Abool.astype(np.int64)
    dp = np.zeros((B, 1 << V, V), dtype=np.int64)
    for v in range(V): dp[:, 1 << v, v] = 1
    for m in range(1, 1 << V):
        if m & (m - 1) == 0: continue
        vs = np.array([v for v in range(V) if m >> v & 1])
        prev = dp[:, m ^ (1 << vs), :]                       # (B, k, V)
        dp[:, m, vs] = np.einsum("bku,buk->bk", prev, A[:, :, vs])
    return dp[:, FULL, :].sum(1) // 2

def batch_edge_conn(Abool):
    out = np.zeros(Abool.shape[0], dtype=np.int64)
    for b in range(Abool.shape[0]):
        G = nx.from_numpy_array(Abool[b].astype(int))
        out[b] = nx.edge_connectivity(G) if nx.is_connected(G) else 0
    return out

def batch_components(spec):
    return (spec < 1e-9).sum(1)

U_STATS = ("deg_var", "lambda2", "log_tau", "triangles", "edge_conn", "components", "ham_paths")

def null_unweighted(n, m, rng, chunk=200, only=U_STATS):
    stats = {k: [] for k in only}
    seqs = []
    done = 0
    while done < n:
        b = min(chunk, n - done)
        vals = np.zeros((b, 91))
        for r in range(b):
            vals[r, rng.choice(91, m, replace=False)] = 1
        W = batch_adj(vals)
        spec, logtau = batch_spectral(W)
        deg = W.sum(2)
        Ab = W > 0
        calc = {"deg_var": lambda: deg.var(1), "lambda2": lambda: spec[:, 1], "log_tau": lambda: logtau,
                "triangles": lambda: np.round(np.einsum("bij,bjk,bki->b", W, W, W) / 6),
                "edge_conn": lambda: batch_edge_conn(Ab), "components": lambda: batch_components(spec),
                "ham_paths": lambda: batch_ham_paths(Ab)}
        for k in only:
            stats[k].append(calc[k]())
        seqs.append(deg.astype(int))
        done += b
    return {k: np.concatenate(v) for k, v in stats.items()}, np.concatenate(seqs)

def null_weighted(stream, n, rng, chunk=5000):
    base = np.array(stream, dtype=float)
    stats = {k: [] for k in ("strength_var", "lambda2", "lambda_max", "log_tau_w")}
    seqs = []
    done = 0
    while done < n:
        b = min(chunk, n - done)
        vals = np.stack([rng.permutation(base) for _ in range(b)])
        W = batch_adj(vals)
        spec, logtau = batch_spectral(W)
        s = W.sum(2)
        stats["strength_var"].append(s.var(1)); stats["lambda2"].append(spec[:, 1])
        stats["lambda_max"].append(spec[:, -1]); stats["log_tau_w"].append(logtau)
        seqs.append(np.round(s).astype(int))
        done += b
    return {k: np.concatenate(v) for k, v in stats.items()}, np.concatenate(seqs)

def two_sided_p(null, obs):
    n = len(null)
    lo = (np.sum(null <= obs + 1e-9) + 1) / (n + 1)
    hi = (np.sum(null >= obs - 1e-9) + 1) / (n + 1)
    return float(min(1.0, 2 * min(lo, hi)))

# ---------------------------------------------------------------- text renderings

def renderings(seq):
    a0 = "".join(chr(65 + x % 26) for x in seq)
    a1 = "".join(chr(65 + (x - 1) % 26) for x in seq)       # 1 -> A, 26 -> Z, 0 -> Z
    return {"a0": a0, "a0_rev": a0[::-1], "a1": a1, "a1_rev": a1[::-1]}

def words_in(seq):
    return sorted({(w, k) for k, s in renderings(seq).items() for w in TARGET_WORDS if w in s})

def null_word_rate(seqs):
    hits = sum(1 for s in seqs if words_in(list(s)))
    return hits / len(seqs), hits

# ---------------------------------------------------------------- crypto check

def crypto_check(cands, scalars):
    import gate, aes_try, btc_addr, p32t_freeze
    assert aes_try.self_test() and btc_addr.self_test() and p32t_freeze.self_test(), "self-test failed"
    targets = aes_try.load_targets(); t = targets["inner96"]
    tot = pads = hits = 0; hit_list = []
    with open(OUT, "w") as f:
        for label, c in cands:
            dec = gate.run_decrypts(c, targets)
            sca = gate.run_scalars(c)
            comp, unc = btc_addr.addrs(int(gate.sha256hex(c), 16))
            better = BETTER in (comp, unc); prize = gate.PRIZE in (comp, unc)
            frz = []
            for form in gate.FORMS:
                pw = c if form == "raw" else gate.sha256hex(c)
                for kdf in gate.KDFS:
                    md, kl = aes_try.KDFS[kdf]
                    key, iv = aes_try.evp_bytes_to_key(pw.encode(), t["salt"], md, kl)
                    if p32t_freeze.primary_ok(key) or p32t_freeze.secondary_ok(key):
                        frz.append((form, kdf))
            near = [r for r in dec if r["pad"]]
            h = any(r["hit"] for r in dec) or prize or better or bool(frz)
            tot += len(dec); pads += len(near); hits += h
            if h: hit_list.append(label)
            f.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "label": label,
                                "candidate": c, "decrypts": dec, "scalars": sca, "addr_comp": comp,
                                "addr_unc": unc, "better": better, "prize": prize, "freeze": frz,
                                "HIT": h}) + "\n")
        sc_hits = []
        for label, k in scalars:
            kk = k % SECP_N
            if kk == 0: continue
            comp, unc = btc_addr.addrs(kk)
            if gate.PRIZE in (comp, unc) or BETTER in (comp, unc):
                sc_hits.append(label)
            f.write(json.dumps({"label": label, "scalar_int": str(k), "addr_comp": comp, "addr_unc": unc,
                                "HIT": label in sc_hits}) + "\n")
    return {"strings": len(cands), "decrypts": tot, "pkcs7_any": pads, "string_hits": hit_list,
            "scalars": len(scalars), "scalar_hits": sc_hits}

# ---------------------------------------------------------------- self-test

def selftest():
    ok = True
    def chk(label, cond):
        nonlocal ok; ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + label)
    K = lambda n: [(i, j) for i in range(n) for j in range(i + 1, n)]
    A5 = adj_from_edges_n(K(5), 5)
    chk("tau(K5) = 125", spanning_trees(A5) == 125)
    chk("tau(K14) = 14^12", spanning_trees(adj_from_edges(K(14))) == 14 ** 12)
    chk("K5: 60 Hamiltonian paths, 12 cycles", ham_paths_and_cycles(A5) == (60, 12))
    chk("K8: 20160 paths, 2520 cycles", ham_paths_and_cycles(adj_from_edges_n(K(8), 8)) == (20160, 2520))
    C7 = adj_from_edges_n([(i, (i + 1) % 7) for i in range(7)], 7)
    chk("C7: tau 7, 7 paths, 1 cycle", spanning_trees(C7) == 7 and ham_paths_and_cycles(C7) == (7, 1))
    P = nx.petersen_graph(); AP = nx.to_numpy_array(P, dtype=int).tolist()
    chk("Petersen: tau 2000, 0 Hamiltonian cycles", spanning_trees(AP) == 2000 and ham_paths_and_cycles(AP)[1] == 0)
    chk("weighted K3 (2,3,5): tau_w = 2*3+3*5+5*2 = 31",
        spanning_trees([[0, 2, 3], [2, 0, 5], [3, 5, 0]]) == 31)
    rng = np.random.default_rng(1)
    agree = True
    for _ in range(40):                      # brute force vs DP on random 7-vertex graphs
        e = [x for x in K(7) if rng.random() < 0.5]; A = adj_from_edges_n(e, 7)
        bp = sum(1 for p in itertools.permutations(range(7)) if p[0] < p[-1]
                 and all(A[p[k]][p[k + 1]] for k in range(6)))
        bc = sum(1 for p in itertools.permutations(range(1, 7)) if p[0] < p[-1]
                 and A[0][p[0]] and A[p[-1]][0] and all(A[p[k]][p[k + 1]] for k in range(5)))
        agree = agree and ham_paths_and_cycles(A) == (bp, bc)
    chk("DP == brute force on 40 random 7-vertex graphs", agree)
    vals = np.zeros((6, 91))
    for r in range(6): vals[r, rng.choice(91, 33, replace=False)] = 1
    Ab = batch_adj(vals) > 0
    exact = [ham_paths_and_cycles(Ab[r].astype(int).tolist())[0] for r in range(6)]
    chk("batched DP == exact DP on 6 random 33-edge K14 subgraphs", list(batch_ham_paths(Ab)) == exact)
    spec, lt = batch_spectral(batch_adj(vals))
    ex = [spanning_trees(Ab[r].astype(int).tolist()) for r in range(6)]
    chk("batched log tau == exact", all((t == 0 and lt[r] == -np.inf) or abs(math.log(t) - lt[r]) < 1e-8
                                       for r, t in enumerate(ex)))
    o = load_objects()
    chk("objects load; mask 33/58; YOUWON at 21", sum(o["mask"]) == 33 and o["res_txt"][21:27] == "YOUWON")
    chk("24 coloured cells: 12 above, 12 below, none mirrored",
        len(o["colU"]) == 12 and len(o["colL"]) == 12 and
        not ({frozenset(x) for x in o["colU"]} & {frozenset(x) for x in o["colL"]}))
    print("campaign 44 self-test passed:", ok)
    return ok

def adj_from_edges_n(edges, n):
    A = [[0] * n for _ in range(n)]
    for i, j in edges: A[i][j] = A[j][i] = 1
    return A

# ---------------------------------------------------------------- run

def describe():
    o = load_objects()
    print("VIC mask (1 = one-digit code, FUBCDORA):", "".join(map(str, o["mask"])))
    print("residual (DBBI - VIC mod 26):", o["res_txt"])
    for p, e in o["placements"].items():
        print(p, "first 6 edges:", e[:6])
    print("coloured upper:", sorted(o["colU"])); print("coloured lower:", sorted(o["colL"]))
    print("english control windows:", len(english_windows()))

def main():
    if "--selftest" in sys.argv:
        sys.exit(0 if selftest() else 1)
    if "--describe" in sys.argv:
        describe(); return
    assert selftest(), "self-test failed; a null here would mean nothing"
    o = load_objects(); P = o["placements"]; RM = P["RM"]
    rng = np.random.default_rng(SEED)
    summary = {"seed": SEED, "N_null_u": N_NULL_U, "N_null_w": N_NULL_W}

    def bits_rm(edges):
        s = {frozenset(e) for e in edges}
        return "".join("1" if frozenset(e) in s else "0" for e in RM)

    # ---- unweighted graphs
    graphs = {}
    for p, e in P.items():
        graphs[f"VIC33_{p}"] = [e[k] for k in range(91) if o["mask"][k]]
        graphs[f"VIC58_{p}"] = [e[k] for k in range(91) if not o["mask"][k]]
    graphs["COL12U"] = o["colU"]
    graphs["COL12L"] = [(c, r) for r, c in o["colL"]]
    graphs["COL24"] = graphs["COL12U"] + graphs["COL12L"]
    ginv = {g: graph_invariants(e) for g, e in graphs.items()}
    dirdeg = {"out": [sum(1 for r, c in o["colU"] + o["colL"] if r == v) for v in range(V)],
              "in": [sum(1 for r, c in o["colU"] + o["colL"] if c == v) for v in range(V)]}
    summary["graphs"] = ginv; summary["COL24_directed_deg"] = dirdeg

    # ---- weighted streams
    winv = {f"{s}_{p}": weighted_invariants(o["streams"][s], e)
            for s in o["streams"] for p, e in P.items()}
    summary["weighted"] = winv

    # ---- A. structure
    t0 = time.time()
    nu, nu_seqs = null_unweighted(N_NULL_U, 33, rng)
    summary["null_u_seconds"] = round(time.time() - t0, 1)
    fam_u = []
    for p in P:
        g = ginv[f"VIC33_{p}"]
        for k in nu:
            fam_u.append({"graph": f"VIC33_{p}", "inv": k, "obs": g[k], "p": two_sided_p(nu[k], g[k]),
                          "null_median": float(np.median(nu[k][np.isfinite(nu[k])]))})
    thr_u = ALPHA / len(fam_u)
    fam_w = []
    nw_seqs = {}
    for s, stream in o["streams"].items():
        nw, nw_seqs[s] = null_weighted(stream, N_NULL_W, rng)
        for p in P:
            w = winv[f"{s}_{p}"]
            for k in nw:
                fam_w.append({"stream": f"{s}_{p}", "inv": k, "obs": w[k], "p": two_sided_p(nw[k], w[k]),
                              "null_median": float(np.median(nw[k][np.isfinite(nw[k])]))})
    thr_w = ALPHA / len(fam_w)
    flagged = [r for r in fam_u if r["p"] < thr_u] + [r for r in fam_w if r["p"] < thr_w]
    summary["structure"] = {"family_u": fam_u, "thr_u": thr_u, "family_w": fam_w, "thr_w": thr_w,
                            "min_p_u": min(r["p"] for r in fam_u), "min_p_w": min(r["p"] for r in fam_w),
                            "flagged": flagged}

    # ---- A'. English control, only if a text-derived object is flagged
    text_derived = [r for r in flagged if r.get("graph", "").startswith("VIC") or
                    r.get("stream", "").split("_")[0] in ("VIC", "RES")]
    if text_derived:
        summary["english_control"] = english_control(text_derived, P, rng)

    # ---- B. text renderings
    seqs = {}
    for g, inv in ginv.items(): seqs[f"deg:{g}"] = inv["deg"]
    seqs["out:COL24"] = dirdeg["out"]; seqs["in:COL24"] = dirdeg["in"]
    for w, inv in winv.items(): seqs[f"strength:{w}"] = inv["strength"]
    found = {k: words_in(v) for k, v in seqs.items() if words_in(v)}
    rate_u = null_word_rate(nu_seqs)
    rate_w = {s: null_word_rate(x) for s, x in nw_seqs.items()}
    summary["text"] = {"sequences": len(seqs), "found": found,
                       "null_rate_deg33": rate_u, "null_rate_strength": rate_w}

    # ---- C. crypto
    cands, scalars = [], []
    def add(label, c):
        if c not in {x for _, x in cands}: cands.append((label, c))
    for g, inv in ginv.items():
        b = bits_rm(graphs[g])
        add(f"{g}:rmbits", b)
        add(f"{g}:rmhex", f"{int(b + '00000', 2):024x}")
        add(f"{g}:deg", ",".join(map(str, inv["deg"])))
        add(f"{g}:tau", str(inv["tau"]))
        add(f"{g}:ham_paths", str(inv["ham_paths"]))
        scalars += [(f"{g}:tau", inv["tau"]), (f"{g}:ham_paths", inv["ham_paths"]), (f"{g}:rmbits_int", int(b, 2))]
    for w, inv in winv.items():
        s, p = w.split("_")
        add(f"{w}:strength", ",".join(map(str, inv["strength"])))
        add(f"{w}:tau_w", str(inv["tau_w"]))
        scalars.append((f"{w}:tau_w", inv["tau_w"]))
        if p != "RM":
            pos = {frozenset(e): k for k, e in enumerate(P[p])}
            reread = "".join(o["alph"][s][o["streams"][s][pos[frozenset(e)]]] for e in RM)
            add(f"{w}:rm_reread", reread)
    seen = set(); scalars = [(l, k) for l, k in scalars if not (k in seen or seen.add(k))]
    summary["crypto"] = crypto_check(cands, scalars)

    json.dump(summary, open(SUMMARY, "w"), indent=1, default=str)
    report(summary)

def zscore(null, obs, inv):
    f = (lambda x: np.exp(x)) if inv.startswith("log_tau") else (lambda x: x)
    x = f(np.asarray(null, dtype=float)); o = float(f(np.float64(obs)))
    sd = x.std()
    return 0.0 if sd == 0 else (o - x.mean()) / sd

def english_control(flags, P, rng, n_null=1000):
    """Pre-registered: a flag on a text-derived object (VIC mask, VIC letters, residual) stands
    only if its |z| against its own null exceeds the 99th percentile of |z| over the 200
    English control windows (creator-log letters), each scored the same way against its own
    null. Otherwise it is attributed to English sequential statistics and withdrawn."""
    wins = english_windows()
    out = []
    for r in flags:
        name = r.get("graph") or r["stream"]; p = name.split("_")[-1]; inv = r["inv"]
        e = P[p]; zs = []
        for wtxt in wins:
            if name.startswith("VIC33"):
                mk = [1 if ch in "FUBCDORA" else 0 for ch in wtxt]
                if sum(mk) == 0: continue
                gi = graph_invariants([e[k] for k in range(91) if mk[k]])
                nu, _ = null_unweighted(n_null, sum(mk), rng, only=(inv,))
                zs.append(abs(zscore(nu[inv], gi[inv], inv)))
            else:
                st = [ord(ch) - 64 for ch in wtxt]
                wi = weighted_invariants(st, e); nw, _ = null_weighted(st, n_null, rng)
                zs.append(abs(zscore(nw[inv], wi[inv], inv)))
        if name.startswith("VIC33"):
            nu, _ = null_unweighted(n_null, 33, rng, only=(inv,)); z_obs = abs(zscore(nu[inv], r["obs"], inv))
        else:
            s0 = name.split("_")[0]
            nw, _ = null_weighted(load_objects()["streams"][s0], n_null, rng); z_obs = abs(zscore(nw[inv], r["obs"], inv))
        q99 = float(np.percentile(zs, 99))
        out.append({"flag": r, "windows": len(zs), "z_obs": z_obs, "control_z_q99": q99,
                    "control_z_max": float(max(zs)), "stands": z_obs > q99})
    return out

def report(s):
    st = s["structure"]
    print("\n== A. structure")
    print(f"unweighted family: {len(st['family_u'])} tests, threshold {st['thr_u']:.2e}, min p {st['min_p_u']:.2e}")
    for r in sorted(st["family_u"], key=lambda r: r["p"])[:8]:
        print(f"   {r['graph']:10s} {r['inv']:11s} obs={r['obs']!s:>22} null_med={r['null_median']:.4g} p={r['p']:.3g}")
    print(f"weighted family:   {len(st['family_w'])} tests, threshold {st['thr_w']:.2e}, min p {st['min_p_w']:.2e}")
    for r in sorted(st["family_w"], key=lambda r: r["p"])[:8]:
        print(f"   {r['stream']:10s} {r['inv']:13s} obs={r['obs']!s:>22} null_med={r['null_median']:.4g} p={r['p']:.3g}")
    print("flagged:", len(st["flagged"]))
    if "english_control" in s:
        for c in s["english_control"]: print("   english control:", json.dumps(c)[:300])
    print("\n== observed graphs")
    for g, inv in s["graphs"].items():
        print(f"   {g:10s} m={inv['edges']:2d} comp={inv['components']} lam={inv['edge_conn']} kap={inv['vertex_conn']} "
              f"tri={inv['triangles']:3d} tau={inv['tau']} ham_p={inv['ham_paths']} ham_c={inv['ham_cycles']} "
              f"diam={inv['diameter']} bip={inv['bipartite']} deg={inv['deg']}")
    t = s["text"]
    print("\n== B. text:", t["sequences"], "sequences x 4 renderings; found:", t["found"] or "none")
    print("   null rate (33-edge degree seqs):", t["null_rate_deg33"])
    print("   null rate (strength seqs):", {k: round(v[0], 5) for k, v in t["null_rate_strength"].items()})
    c = s["crypto"]
    print(f"\n== C. crypto: {c['strings']} strings, {c['decrypts']} decrypts, pkcs7_any={c['pkcs7_any']}, "
          f"string hits={c['string_hits'] or 0}; {c['scalars']} scalars, scalar hits={c['scalar_hits'] or 0}")

if __name__ == "__main__":
    main()
