# -*- coding: utf-8 -*-
"""windows_dry.json 의 빈 원본 구간(앞뒤 3초 빼고)에 소리만 살린 장면 A 를 채운다 — 큰 구간부터, 목표 초까지.
이야기 순서: 그 원본 초보다 앞선 마지막 줄(N 구간 시작·D 첫 말·A 시작) 뒤에 끼운다. 사용: python addA.py 목표초 [첫초 끝초 [빈틈초=12]]"""
import ast, json, sys
GOAL = float(sys.argv[1]); LO = float(sys.argv[2]) if len(sys.argv) > 2 else 37; HI = float(sys.argv[3]) if len(sys.argv) > 3 else 5445
GAP = float(sys.argv[4]) if len(sys.argv) > 4 else 12   # 14v2 10-17: 빈틈이 모자라면 9.5 까지 낮춘다
W = json.load(open("windows_dry.json", encoding="utf-8"))
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
sp = sorted((w["s"], w["s"] + (w["b"] - w["a"]) * w.get("rate", 1.05 if w["kind"] == "A" else 1.0)) for w in W)
gaps = [(b1 + 3.2, a2 - 3.2) for (a1, b1), (a2, b2) in zip(sp, sp[1:]) if a2 - b1 > GAP and LO < b1 < HI]
gaps.sort(key=lambda g: -(g[1] - g[0]))
new = []; tot = 0
for a, b in gaps:
    x = a
    while x + 2.4 <= b and tot < GOAL:
        new.append((x, min(b, x + 2.6))); tot += 2.3; x += 2.4 + 3.2
    if tot >= GOAL: break
src = open("script.py", encoding="utf-8").read(); lines = src.splitlines(keepends=True)
SE = [n.value for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "S"][0].elts
ns = {}; exec(src, ns); S = ns["S"]
zone = None; tk = []
for k, x in enumerate(S):
    if x[0] == "ZONE": zone = x[1]; continue
    if zone != "main": continue
    if x[0] == "N": t = x[2][0][0] if isinstance(x[2], (list, tuple)) else x[2]
    elif x[0] == "D": t = min(L[i]["ws"] for i in x[1])
    elif x[0] == "A": t = x[1]
    else: continue
    tk.append((t, k))
ins = {}
for a, b in new:
    prev = [k for t, k in tk if t <= a]
    if not prev: continue
    ins.setdefault(max(prev), []).append(f'("A", {a:.1f}, {b:.1f}, 2.3),   # 빈 구간 채움(addA)\n')
for k in sorted(ins, reverse=True):
    e = SE[k]; lines[e.end_lineno:e.end_lineno] = sorted(ins[k])
open("script.py", "w", encoding="utf-8").write("".join(lines))
print("A", sum(len(v) for v in ins.values()), f"· 약 {tot:.0f}초")
