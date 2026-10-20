# -*- coding: utf-8 -*-
# 실패한 나레 줄 k 들 — 그 구간(±3초) 안에 원본을 쓰는 다른 줄들 (14v2 10-17). 사용: python -X utf8 near.py k1 k2 ... (plan 이 「놓을 자리 없음」이라 한 줄 번호 — windows.json 기준)
import json, sys
ns = {}; exec(open("script.py", encoding="utf-8").read(), ns); S = ns["S"]
L = {x["id"]: x for x in json.load(open("lines.json", encoding="utf-8"))}
W = json.load(open("windows.json", encoding="utf-8"))
for k in map(int, sys.argv[1:]):
    x = S[k]
    if x[0] == "A": rr = [(x[1], x[2])]
    elif x[0] == "N": rr = x[2] if isinstance(x[2], list) else [(x[2], x[3])]
    else: print(f"== 줄{k} {x[0]} — 나레·A 줄만 본다"); continue
    print(f"== 줄{k} {x[1][:40]} {rr}")
    for a, b in rr:
        for w in sorted(W, key=lambda w: w["s"]):
            if w["k"] != k and a - 3 < w["s"] < b + 3:
                y = S[w["k"]]; print(f"   s{w['s']:.1f} 줄{w['k']} {y[0]} {str(y[1])[:40]} {y[2] if y[0] == 'D' else ''}")
