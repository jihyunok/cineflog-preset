# -*- coding: utf-8 -*-
"""대본의 대사(D) 줄을 dcand.txt 와 맞대어 ✗ 인 줄마다 그 줄을 포함한(또는 바로 옆) ✓ 대안을 보여 준다. 사용: python dfix.py"""
import json, re
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
C = {}
for l in open("dcand.txt", encoding="utf-8"):
    p = l.rstrip("\n").split("|", 4)
    if len(p) < 5: continue
    ids = tuple(json.loads(p[0])) if p[0].startswith("[") else (int(p[0]),)
    C[ids] = (p[1], p[2], p[3], p[4])
bad = 0
for k, x in enumerate(ns["S"]):
    if x[0] != "D": continue
    ids = tuple(x[1]) if isinstance(x[1], list) else (x[1],)
    c = C.get(ids)
    if c and c[2] == "✓": continue
    bad += 1
    print(f"줄{k} D {list(ids)} 「{x[2]}」 → {c[2] if c else '후보표에 없음(길이 넘음·욕·3줄 넘는 묶음)'}")
    alt = [(i, v) for i, v in C.items() if v[2] == "✓" and (set(i) & set(ids) or min(abs(a - b) for a in i for b in ids) <= 1)]
    for i, v in sorted(alt)[:8]: print(f"      ✓ {list(i)} {v[0]} {v[1]}s {v[3][:90]}")
sp = []
for k, x in enumerate(ns["S"]):
    if x[0] == "D":
        ids = tuple(x[1]) if isinstance(x[1], list) else (x[1],)
        c = C.get(ids)
        if c:
            a, b = c[0].split(":"); t = int(a) * 60 + float(b); sp.append((t, t + float(c[1]), k, list(ids)))
sp.sort(); gapbad = 0
for x, y in zip(sp, sp[1:]):
    if y[0] - x[1] < 3.0 - 0.01: gapbad += 1; print(f"  3초 간격 ✗ 줄{x[2]} {x[3]} → 줄{y[2]} {y[3]} ({y[0] - x[1]:.2f}초)")
print("✗ 대사 줄", bad, "· 3초 간격 ✗", gapbad)
