# -*- coding: utf-8 -*-
"""나레 줄만 — 줄마다 밑에 깔린 조각의 원본 시각 · agy 그림 설명(조각 가운데). 사용: python review_n.py [windows_dry.json] [시작번호]"""
import json, sys
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows_dry.json", encoding="utf-8"))
k0 = int(sys.argv[2]) if len(sys.argv) > 2 else 1
S = json.load(open("shots.json", encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); SC = ns["S"]
def desc(t): return next((x for x in S if x["s"] <= t < x["e"]), {}).get("desc", "?")
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
ni = 0
for k, x in enumerate(SC):
    if x[0] != "N": continue
    ni += 1
    if ni < k0: continue
    ws = [w for w in W if w.get("k") == k]
    print(f"n{ni:03d} 줄{k} {x[1]}")
    for w in ws:
        sl = (w["b"] - w["a"]) * 1.05
        print(f"      {mm(w['s'])} {desc(w['s'] + sl / 2)[:115]}")
