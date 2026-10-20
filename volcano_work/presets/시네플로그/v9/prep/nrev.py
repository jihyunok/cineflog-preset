# -*- coding: utf-8 -*-
# 나레마다 그림 구간 안의 컷 설명(shots.json) — 구간이 그 문장 장면인지 눈으로 보기 (14v2 10-17)
import json, re, sys
S = json.load(open("shots.json", encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns)
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
ni = 0; k0 = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for k, x in enumerate(ns["S"]):
    if x[0] != "N": continue
    ni += 1
    if ni < k0: continue
    rr = x[2] if isinstance(x[2], (list, tuple)) else [(x[2], x[3])]
    print(f"n{ni:03d} {x[1]}")
    for a, b in rr:
        ds = [s for s in S if s["e"] > a and s["s"] < b]
        prev = None
        if len(ds) > 6: ds = [ds[int(i * (len(ds) - 1) / 5)] for i in range(6)]
        for s in ds:
            d = re.sub(r"^(In|At|On|Inside|Outside) [^,]*, ", "", s.get("desc", "?"))[:80]
            if d == prev: continue
            print(f"   {s['s']:.0f} {d}"); prev = d
