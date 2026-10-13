# -*- coding: utf-8 -*-
"""ep02.S → items.json (나레 조각 + 원본 대사) · 대사 간격·길이 검사"""
import json, re, sys, importlib, ep02
S = json.load(open("subs_ko.json", encoding="utf-8"))
items = []; rng = None; ni = 0
for x in ep02.S:
    if x[0] == "R": rng = [x[1], x[2]]; continue
    ni += 1; items.append({"type": "N", "ni": ni, "text": x[0], "rng": rng})
    d = x[1]
    if d is None: continue
    d = d if isinstance(d, tuple) else (d,)
    i = d[0]; q = S[i - 1]; nx = S[i]["s"] if i < len(S) else 1e9
    txt = d[1] if len(d) > 1 else q["t"]
    txt = re.sub(r"^- ", "", txt).replace(" - ", " ").strip("'\"")
    ln = min(q["e"] - q["s"] + 0.2, nx - q["s"] - 0.05)
    if len(d) > 2: ln = d[2]
    mirror = ln > 2.9
    ln = min(ln, 3.9 if mirror else 2.9)
    items.append({"type": "D", "i": i, "s": round(q["s"] - 0.05, 3), "d": round(ln, 2), "ko": txt, "mirror": mirror})
ds = sorted((q["s"], q["s"] + q["d"], q["i"]) for q in items if q["type"] == "D")
bad = 0
for a, b in zip(ds, ds[1:]):
    if b[0] - a[1] < 3.0: print("간격", a[2], b[2], round(b[0] - a[1], 2)); bad += 1
for q in items:
    if q["type"] == "D" and len(q["ko"]) > 24: print("김", q["i"], q["ko"]); bad += 1
json.dump(items, open("items.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("나레", ni, "대사", len(ds), "대사합", round(sum(b - a for a, b, _ in ds), 1), "문제", bad)
