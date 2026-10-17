# -*- coding: utf-8 -*-
"""문제 D 줄마다 그 자막(srt.txt) 시각 ±2.5초 안의 ✓ 대안(dcand)과 영어·한국어 자막을 보여 준다(03v2 10-17). 사용: python -X utf8 dalt.py > _dalt.txt"""
# 문제 D 줄마다: 그 자막 시각 ±2초 안의 ✓ 후보(dcand)와 영어·한국어 자막
import json, re, sys
src = open("script.py", encoding="utf-8").read()
ns = {}; exec(src, ns)
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
K = {}
for r in open("srt.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("\t"); K[int(p[0])] = (float(p[1]), float(p[2]), p[3])
C = []
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    ids = json.loads(p[0]) if p[0].startswith("[") else [int(p[0])]
    C.append((ids, float(p[2]), p[3], p[4]))
KO = {}
for r in open("lines_ko.txt", encoding="utf-8"):
    p = r.rstrip("\n").split("|"); KO[int(p[0])] = p[-1]
cand = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    cand[p[0]] = p[3]
import ast
T = ast.parse(src); SE = [n.value for n in T.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
SRI = [[a.value for a in e.elts[1].args] if isinstance(e, ast.Tuple) and len(e.elts) > 1 and isinstance(e.elts[1], ast.Call) else None for e in SE]
di = 0
for k, x in enumerate(ns["S"]):
    if x[0] != "D": continue
    idx = SRI[k]
    ids = x[1]
    ok = False
    if ids:
        ws = min(L[i]["ws"] for i in ids if L[i]["ws"] is not None); we = max(L[i]["we"] for i in ids if L[i]["we"] is not None)
        key = str(ids[0]) if len(ids) == 1 else json.dumps(ids)
        ok = we - ws <= 3.15 and "✓" in cand.get(key, "")
    if ok: continue
    a = min(K[i][0] for i in idx); b = max(K[i][1] for i in idx)
    print(f"■ k{k} sr{idx} {a:.1f}~{b:.1f} 「{x[2]}」  ko: {' // '.join(K[i][2] for i in idx)}")
    for ids2, du, st, en in C:
        s0 = L[ids2[0]]["s"]; e0 = L[ids2[-1]]["e"]
        if "✓" in st and s0 < b + 2.5 and e0 > a - 2.5:
            print(f"   ✓ {ids2} {du:.2f}s {en[:90]}  ‖ {' / '.join(KO.get(i,'') for i in ids2)[:80]}")
