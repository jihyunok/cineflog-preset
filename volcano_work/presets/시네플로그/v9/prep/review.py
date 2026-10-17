# -*- coding: utf-8 -*-
"""대본 줄마다 밑에 깔린 조각의 원본 그림 설명(agy) — 「나레가 말하는 장면이 그 밑에」 눈으로 확인. 사용: python review.py [windows_dry.json]"""
import json, sys
W = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "windows_dry.json", encoding="utf-8"))
S = json.load(open("shots.json", encoding="utf-8")); ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); SC = ns["S"]
def desc(t):
    x = next((x for x in S if x["s"] <= t < x["e"]), None); return (x or {}).get("desc", "?")
def mm(t): return f"{int(t // 60)}:{t % 60:04.1f}"
for k, x in enumerate(SC):
    ws = [w for w in W if w.get("k") == k]
    if not ws: continue
    head = "N " + x[1] if x[0] == "N" else "D " + x[2] if x[0] == "D" else "A (소리)"
    print(f"{mm(ws[0]['a'])} {head}")
    for w in ws: print(f"      {mm(w['s'])} {desc(w['s'] + 0.8)[:120]}")
