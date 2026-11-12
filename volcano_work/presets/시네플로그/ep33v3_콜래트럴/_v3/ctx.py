# -*- coding: utf-8 -*-
"""33 v3: 나레 블록(ni) 맥락 — 대본 줄·문장 구간·앞뒤 대사 원본·조각·컷 설명·판정 줄.  python ctx.py <ni> [<ni>...] [--shots]"""
import ast, csv, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
WK = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ns = {}; exec(open(os.path.join(WK, "script.py"), encoding="utf-8").read(), ns); S = ns["S"]
L = {l["id"]: l for l in json.load(open(os.path.join(WK, "lines.json"), encoding="utf-8"))}
SH = json.load(open(os.path.join(WK, "shots.json"), encoding="utf-8"))
W = json.load(open(os.path.join(WK, "windows.json"), encoding="utf-8"))
CSV = os.environ.get("CSV", r"D:\cine_work\재검사_1107\ep33v2_재검사95\줄별_화면판정.csv")
rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))
def mm(t): return f"{int(t//60)}:{t%60:04.1f}"
def dsrc(x): ids = x[1]; return (min(L[i]["s"] for i in ids), max(L[i]["e"] for i in ids))
nis = []; n = 0
for k, x in enumerate(S):
    if x[0] == "N": n += 1; nis.append((n, k))
want = [int(a) for a in sys.argv[1:] if a.isdigit()]
for ni, k in nis:
    if ni not in want: continue
    x = S[k]
    print(f"\n=== 나레 {ni} (줄 k={k}) 「{x[1]}」"); print("   구간", x[2] if len(x) > 2 else "", x[3] if len(x) > 3 and isinstance(x[3], dict) else (x[4] if len(x) > 4 else ""))
    for j in range(max(0, k - 2), min(len(S), k + 3)):
        y = S[j]
        if y[0] == "D": a, b = dsrc(y); print(f"   {'앞' if j < k else '뒤'} D k={j} 원본 {mm(a)}~{mm(b)} ({a:.1f}~{b:.1f}) 「{y[2][:40]}」")
        elif y[0] == "A": print(f"   {'앞' if j < k else '뒤'} A k={j} {y[1]}~{y[2]}")
        elif y[0] == "N" and j != k: print(f"   {'앞' if j < k else '뒤'} N k={j} 「{y[1][:30]}」")
    for w in W:
        if w.get("k") == k: print(f"   조각 화면 {w['a']:.2f}~{w['b']:.2f} 원본 {w['s']:.2f}({mm(w['s'])}) 길이 {w['b']-w['a']:.2f}{' noflip' if w.get('noflip') else ''}")
    for r in rows:
        if r["blk"] == str(ni): print(f"   줄#{r['idx']} {r['start']} src {r['src1']}/{r['src2']} 「{r['text']}」 {r.get('verdict','')} {r.get('note','')[:70]}")
    if "--shots" in sys.argv:
        ss = [w["s"] for w in W if w.get("k") == k]
        lo, hi = min(ss) - 25, max(ss) + 25
        for s in SH:
            if s["e"] > lo and s["s"] < hi: print(f"     shot {s['s']:.1f}-{s['e']:.1f} {s['desc'][:150]}")
